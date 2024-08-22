from fastapi import APIRouter, Depends, File, UploadFile, Request, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from app.auth_utils import verify_token
from app.routers.auth import get_current_user
from app.database import get_db
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
from app import schemas, crud, models
from typing import List
import pandas as pd
import io
import uuid
import time
import boto3
import os
from dotenv import load_dotenv

load_dotenv("../.env")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

filename = ""


@router.get("/landing")
def landing_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated")

    user = get_current_user(token=token, db=db)
    user_uploads = db.query(
        models.Analysis).filter(
        models.Analysis.user_id == user.id).all()
    analysis = db.query(models.Analysis).filter(
        models.Analysis.user_id == user.id).first()

    return templates.TemplateResponse(
        "landing.html", {
            "request": request, "user": user, "uploads": user_uploads, "analysis": analysis})


@router.get("/my-uploads", response_model=List[schemas.AnalysisCreate])
def get_my_uploads(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated")

    user = get_current_user(token=token, db=db)
    user_uploads = db.query(
        models.Analysis).filter(
        models.Analysis.user_id == user.id).all()

    return user_uploads


@router.get("/my-uploads/{analysis_id}", response_model=schemas.AnalysisCreate)
def get_analysis(
        analysis_id: int,
        request: Request,
        db: Session = Depends(get_db)):
    token = request.cookies.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated")

    user = get_current_user(token=token, db=db)
    analysis = db.query(models.Analysis).filter(
        models.Analysis.analysis_id == analysis_id,
        models.Analysis.user_id == user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found")

    return analysis


@router.get("/eda/{analysis_id}")
def eda_page(
        request: Request,
        analysis_id: int,
        db: Session = Depends(get_db)):
    token = request.cookies.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated")

    user = get_current_user(token=token, db=db)

    #analysis = db.query(models.Analysis).filter(
    #    models.Analysis.analysis_id == analysis_id).first()
    analysis = db.query(models.Analysis).filter(
        models.Analysis.user_id == user.id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found")

    s3_key = f"uploads/{user.id}/{analysis.samplesheet_path}"
    csv_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
    csv_data = csv_obj['Body'].read().decode('utf-8')
    df = pd.read_csv(io.StringIO(csv_data), index_col=0)
    df = normalize_to_cpm(df.fillna(0))

    gene_names = df.index.tolist()
    gene_biotypes = (
        db.query(models.Gene.gene_name, models.Gene.biotype)
        .filter(models.Gene.gene_name.in_(gene_names))
        .all()
    )

    biotype_dict = {gene.gene_name: gene.biotype for gene in gene_biotypes}
    df['biotype'] = df.index.map(biotype_dict.get)
    df = df.dropna(subset=['biotype'])

    coding_genes = df[df['biotype'] == "protein_coding"]
    noncoding_genes = df[df['biotype'] != "protein_coding"]

    num_coding_genes = len(coding_genes)
    num_noncoding_genes = len(noncoding_genes)

    gene_distribution = px.pie(
        names=['Protein Coding', 'Non-Coding'],
        values=[num_coding_genes, num_noncoding_genes],
        title='',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    gene_distribution.update_layout(template="plotly_white")

    tau_coding = coding_genes.apply(
        lambda row: calculate_tau(row[:-1].values), axis=1).tolist()
    tau_noncoding = noncoding_genes.apply(
        lambda row: calculate_tau(row[:-1].values), axis=1).tolist()

    tau_distribution = go.Figure()
    tau_distribution.add_trace(
        go.Box(
            y=tau_coding,
            name="Protein Coding",
            boxmean='sd'))
    tau_distribution.add_trace(
        go.Box(
            y=tau_noncoding,
            name="Non-Coding",
            boxmean='sd'))
    tau_distribution.update_layout(
        title="",
        xaxis_title="Gene biotype",
        yaxis_title="Tissue specificity (Tau)",
        template="plotly_white",
        boxmode='group'
    )

    sample_clustering = (
        db.query(models.SampleClustering)
        .filter(models.SampleClustering.analysis_id == analysis_id)
        .all()
    )

    pca_plot = px.scatter(
        x=[sc.pca1 for sc in sample_clustering],
        y=[sc.pca2 for sc in sample_clustering],
        color=[sc.cluster for sc in sample_clustering],
        hover_name=[sc.sample_id for sc in sample_clustering],
        labels={"x": "PC 1", "y": "PC 2"},
        title="",
        template="plotly_white",
    )
    pca_plot.update_layout(margin=dict(l=20, r=20, t=50, b=20))

    df['stdev'] = df.drop(columns=['biotype']).std(axis=1)
    top_1000_genes = df.nlargest(
        100, 'stdev').drop(
        columns=[
            'stdev', 'biotype'])
    heatmap_data = top_1000_genes.values
    heatmap = ff.create_annotated_heatmap(
        z=heatmap_data,
        x=list(top_1000_genes.columns),
        y=list(top_1000_genes.index),
        colorscale='Viridis',
        showscale=True
    )
    heatmap.update_layout(
        title='',
        template="plotly_white",
        xaxis={'side': 'bottom', 'tickangle': -45, 'tickfont': {'size': 10}},
        yaxis={'tickfont': {'size': 10}}
    )

    return templates.TemplateResponse("eda.html", {
        "request": request,
        "gene_distribution": gene_distribution.to_html(full_html=False),
        "tau_distribution": tau_distribution.to_html(full_html=False),
        "pca_plot": pca_plot.to_html(full_html=False),
        "heatmap": heatmap.to_html(full_html=False),
    })


@router.get("/eda")
def eda_page_na(
        request: Request,
        analysis_id: int,
        db: Session = Depends(get_db)):
    token = request.cookies.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated")

    user = get_current_user(token=token, db=db)

    analysis = db.query(models.Analysis).filter(
        models.Analysis.user_id == user.id).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found")
    
    eda_page(request, analysis, db)


def normalize_to_cpm(counts_df):
    counts_df = counts_df[counts_df.max(axis=1) > 0]
    total_counts_per_sample = counts_df.sum(axis=0)
    cpm_df = counts_df.div(total_counts_per_sample, axis=1) * 1e6

    print(cpm_df.head())

    return cpm_df


@router.post("/upload-file")
async def upload_file(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    token = request.cookies.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated")

    user = get_current_user(token=token, db=db)

    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a CSV file.")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content), index_col=0)
        df.fillna(0, inplace=True)
        df = normalize_to_cpm(df)

        global filename
        filename = file.filename
        s3_key = f"uploads/{user.id}/{file.filename}"
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=content)

    except pd.errors.ParserError:
        raise HTTPException(
            status_code=400,
            detail="Error parsing CSV file. Please ensure it is correctly formatted.")

    analysis_record = crud.create_analysis(
        db=db,
        analysis=schemas.AnalysisCreate(
            logic_name="User Uploaded Analysis",
            samplesheet_path=file.filename,
            analysis_date=None,
            analysis_parameters=None,
            metadata_id=None
        ),
        user_id=user.id
    )

    background_tasks.add_task(
        perform_clustering,
        db,
        df,
        analysis_record.analysis_id)
    background_tasks.add_task(
        derive_metrics,
        db,
        df,
        analysis_record.analysis_id)
    background_tasks.add_task(save_to_db, db, df, analysis_record.analysis_id)

    table_data = {
        "columns": df.columns.tolist(),
        "rows": df.reset_index().values.tolist()
    }

    sample_summary = []
    for col in df.columns:
        summary = {
            "sample": col,
            "statistics": df[col].describe().to_json()
        }
        sample_summary.append(summary)

    return JSONResponse(
        content={
            "tableData": table_data,
            "sampleSummary": sample_summary,
            "analysisId": analysis_record.analysis_id})


def save_to_db(db: Session, df: pd.DataFrame, analysis_id: int):
    for sample_id in df.columns:
        existing_sample = db.query(models.Sample).filter(
            models.Sample.sample_id == sample_id).first()
        if not existing_sample:
            new_sample = models.Sample(
                sample_id=sample_id,
                sample_description="",
                sample_type="",
                sample_source=""
            )
            db.add(new_sample)

    db.commit()

    gene_expressions = []
    for gene_name, row in df.iterrows():
        for sample_id, raw_count in row.items():
            gene_expressions.append({
                "raw_count": raw_count,
                "TPM": None,
                "FPKM": None,
                "RPKM": None,
                "gene_name": gene_name,
                "sample_id": sample_id,
                "analysis_id": analysis_id
            })

    db.bulk_insert_mappings(models.GeneExpression, gene_expressions)
    db.commit()


def perform_clustering(db: Session, df: pd.DataFrame, analysis_id: int):
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(df.T)

    kmeans = KMeans(n_clusters=3)
    clusters = kmeans.fit_predict(pca_result)

    for idx, sample_id in enumerate(df.columns):
        clustering_record = schemas.SampleClusteringCreate(
            sample_id=sample_id,
            pca1=pca_result[idx, 0],
            pca2=pca_result[idx, 1],
            cluster=clusters[idx],
            analysis_id=analysis_id
        )
        crud.create_sample_clustering(db=db, clustering=clustering_record)


def derive_metrics(db: Session, df: pd.DataFrame, analysis_id: int):
    gene_names = df.index.tolist()
    gene_biotypes = (
        db.query(
            models.Gene.gene_name,
            models.Gene.biotype) .filter(
            models.Gene.gene_name.in_(gene_names),
            models.Gene.biotype.in_(
                [
                    "protein_coding",
                    "lncRNA",
                    "processed_pseudogene",
                    "unprocessed_pseudogene"])) .all())

    biotype_dict = {gene.gene_name: gene.biotype for gene in gene_biotypes}
    df['biotype'] = df.index.map(biotype_dict.get)
    df = df.dropna(subset=['biotype'])

    specificity_records = []
    complexity_records = []

    for gene_name in df.index:
        tau = calculate_tau(df.loc[gene_name, df.columns[:-1]].values)
        specificity_record = schemas.TissueSpecificityCreate(
            gene_name=gene_name,
            tau=tau,
            analysis_id=analysis_id
        )
        specificity_records.append(specificity_record)

    try:
        crud.bulk_create_tissue_specificity(
            db=db, tissue_specificity_records=specificity_records)
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error inserting tissue specificity records: {e}")
        return

    for sample_id in df.columns[:-1]:
        total_reads = int(df[sample_id].sum())
        biotype_groups = df.groupby('biotype')[sample_id].sum()

        for biotype, reads in biotype_groups.items():
            proportion = reads / total_reads
            complexity_record = schemas.TissueComplexityCreate(
                sample_id=sample_id,
                gene_biotype=biotype,
                proportion=proportion,
                total_reads=total_reads,
                analysis_id=analysis_id
            )
            complexity_records.append(complexity_record)

    try:
        crud.bulk_create_tissue_complexity(
            db=db, tissue_complexity_records=complexity_records)
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error inserting tissue complexity records: {e}")
        return

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error during commit: {e}")


def calculate_tau(expression_values):
    # print(expression_values)
    max_expression = max(expression_values)
    return sum((1 - (expression / max_expression))
               for expression in expression_values) / (len(expression_values) - 1)
