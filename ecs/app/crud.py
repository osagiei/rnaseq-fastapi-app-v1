from sqlalchemy.orm import Session
from app import models, schemas
from app.auth_utils import get_password_hash
import pandas as pd


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = user.password  # get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_gene(db: Session, coord_id: str):
    return db.query(
        models.Gene).filter(
        models.Gene.coord_id == coord_id).first()


def get_genes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Gene).offset(skip).limit(limit).all()


def create_gene(db: Session, gene: schemas.GeneCreate):
    db_gene = models.Gene(**gene.dict())
    db.add(db_gene)
    db.commit()
    db.refresh(db_gene)
    return db_gene


def update_gene(db: Session, coord_id: str, gene: schemas.GeneCreate):
    db_gene = get_gene(db, coord_id)
    if db_gene is None:
        return None
    for key, value in gene.dict().items():
        setattr(db_gene, key, value)
    db.commit()
    return db_gene


def delete_gene(db: Session, coord_id: str):
    db_gene = get_gene(db, coord_id)
    if db_gene:
        db.delete(db_gene)
        db.commit()
        return db_gene
    return None


def get_gene_expression(db: Session, gene_expression_id: int):
    return db.query(models.GeneExpression).filter(
        models.GeneExpression.gene_expression_id == gene_expression_id).first()


def get_gene_expressions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.GeneExpression).offset(skip).limit(limit).all()


def create_gene_expression(
        db: Session,
        gene_expression: schemas.GeneExpressionCreate):
    db_gene_expression = models.GeneExpression(**gene_expression.dict())
    db.add(db_gene_expression)
    db.commit()
    db.refresh(db_gene_expression)
    return db_gene_expression


def update_gene_expression(
        db: Session,
        gene_expression_id: int,
        gene_expression: schemas.GeneExpressionCreate):
    db_gene_expression = get_gene_expression(db, gene_expression_id)
    if db_gene_expression is None:
        return None
    for key, value in gene_expression.dict().items():
        setattr(db_gene_expression, key, value)
    db.commit()
    return db_gene_expression


def delete_gene_expression(db: Session, gene_expression_id: int):
    db_gene_expression = get_gene_expression(db, gene_expression_id)
    if db_gene_expression:
        db.delete(db_gene_expression)
        db.commit()
        return db_gene_expression
    return None


def get_analysis(db: Session, analysis_id: int):
    return db.query(
        models.Analysis).filter(
        models.Analysis.analysis_id == analysis_id).first()


def get_analyses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Analysis).offset(skip).limit(limit).all()


def get_analyses_by_session_id(db: Session, session_id: str):
    return db.query(
        models.Analysis).filter(
        models.Analysis.session_id == session_id).all()


def create_analysis(
        db: Session,
        analysis: schemas.AnalysisCreate,
        user_id: int):
    db_analysis = models.Analysis(
        **analysis.dict(),
        user_id=user_id
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


def update_analysis(
        db: Session,
        analysis_id: int,
        analysis: schemas.AnalysisCreate):
    db_analysis = get_analysis(db, analysis_id)
    if db_analysis is None:
        return None
    for key, value in analysis.dict().items():
        setattr(db_analysis, key, value)
    db.commit()
    return db_analysis


def delete_analysis(db: Session, analysis_id: int):
    db_analysis = get_analysis(db, analysis_id)
    if db_analysis:
        db.delete(db_analysis)
        db.commit()
        return db_analysis
    return None


def get_sample(db: Session, sample_id: str):
    return db.query(
        models.Sample).filter(
        models.Sample.sample_id == sample_id).first()


def get_samples(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sample).offset(skip).limit(limit).all()


def create_sample(db: Session, sample: schemas.SampleCreate):
    db_sample = models.Sample(**sample.dict())
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


def update_sample(db: Session, sample_id: str, sample: schemas.SampleCreate):
    db_sample = get_sample(db, sample_id)
    if db_sample is None:
        return None
    for key, value in sample.dict().items():
        setattr(db_sample, key, value)
    db.commit()
    return db_sample


def delete_sample(db: Session, sample_id: str):
    db_sample = get_sample(db, sample_id)
    if db_sample:
        db.delete(db_sample)
        db.commit()
        return db_sample
    return None


def update_gene_expression_and_samples(
        db: Session,
        df: pd.DataFrame,
        analysis_id: int):
    for sample_id in df.columns:
        sample = models.Sample(
            sample_id=sample_id,
            sample_description="",
            sample_type="",
            sample_source=""
        )
        db.merge(sample)

    for gene_name, row in df.iterrows():
        for sample_id, raw_count in row.items():
            gene_expression = models.GeneExpression(
                raw_count=raw_count,
                TPM=None,
                FPKM=None,
                RPKM=None,
                gene_name=gene_name,
                sample_id=sample_id,
                analysis_id=analysis_id
            )
            db.add(gene_expression)

    db.commit()


def get_tissue_specificity(db: Session, tissue_specificity_id: int):
    return db.query(models.TissueSpecificity).filter(
        models.TissueSpecificity.tissue_specificity_id == tissue_specificity_id).first()


def get_tissue_specificities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TissueSpecificity).offset(skip).limit(limit).all()


def create_tissue_specificity(
        db: Session,
        tissue_specificity: schemas.TissueSpecificityCreate):
    db_tissue_specificity = models.TissueSpecificity(
        **tissue_specificity.dict())
    db.add(db_tissue_specificity)
    db.commit()
    db.refresh(db_tissue_specificity)
    return db_tissue_specificity


def update_tissue_specificity(
        db: Session,
        tissue_specificity_id: int,
        tissue_specificity: schemas.TissueSpecificityCreate):
    db_tissue_specificity = get_tissue_specificity(db, tissue_specificity_id)
    if db_tissue_specificity is None:
        return None
    for key, value in tissue_specificity.dict().items():
        setattr(db_tissue_specificity, key, value)
    db.commit()
    return db_tissue_specificity


def delete_tissue_specificity(db: Session, tissue_specificity_id: int):
    db_tissue_specificity = get_tissue_specificity(db, tissue_specificity_id)
    if db_tissue_specificity:
        db.delete(db_tissue_specificity)
        db.commit()
        return db_tissue_specificity
    return None


def create_sample_clustering(db: Session,
                             clustering: schemas.SampleClusteringCreate):
    db_clustering = models.SampleClustering(**clustering.dict())
    db.add(db_clustering)
    db.commit()
    db.refresh(db_clustering)
    return db_clustering


def get_tissue_complexity(db: Session, tissue_complexity_id: int):
    return db.query(models.TissueComplexity).filter(
        models.TissueComplexity.tissue_complexity_id == tissue_complexity_id).first()


def get_tissue_complexities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TissueComplexity).offset(skip).limit(limit).all()


def create_tissue_complexity(
        db: Session,
        tissue_complexity: schemas.TissueComplexityCreate):
    db_tissue_complexity = models.TissueComplexity(**tissue_complexity.dict())
    db.add(db_tissue_complexity)
    db.commit()
    db.refresh(db_tissue_complexity)
    return db_tissue_complexity


def update_tissue_complexity(
        db: Session,
        tissue_complexity_id: int,
        tissue_complexity: schemas.TissueComplexityCreate):
    db_tissue_complexity = get_tissue_complexity(db, tissue_complexity_id)
    if db_tissue_complexity is None:
        return None
    for key, value in tissue_complexity.dict().items():
        setattr(db_tissue_complexity, key, value)
    db.commit()
    return db_tissue_complexity


def delete_tissue_complexity(db: Session, tissue_complexity_id: int):
    db_tissue_complexity = get_tissue_complexity(db, tissue_complexity_id)
    if db_tissue_complexity:
        db.delete(db_tissue_complexity)
        db.commit()
        return db_tissue_complexity
    return None


def get_metadata(db: Session, metadata_id: int):
    return db.query(
        models.Metadata).filter(
        models.Metadata.metadata_id == metadata_id).first()


def get_all_metadata(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Metadata).offset(skip).limit(limit).all()


def create_metadata(db: Session, metadata: schemas.MetadataCreate):
    db_metadata = models.Metadata(**metadata.dict())
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)
    return db_metadata


def update_metadata(
        db: Session,
        metadata_id: int,
        metadata: schemas.MetadataCreate):
    db_metadata = get_metadata(db, metadata_id)
    if db_metadata is None:
        return None
    for key, value in metadata.dict().items():
        setattr(db_metadata, key, value)
    db.commit()
    return db_metadata


def delete_metadata(db: Session, metadata_id: int):
    db_metadata = get_metadata(db, metadata_id)
    if db_metadata:
        db.delete(db_metadata)
        db.commit()
        return db_metadata
    return None


def bulk_create_tissue_specificity(
        db: Session,
        tissue_specificity_records: list):
    db_records = [
        models.TissueSpecificity(
            **record.dict()) for record in tissue_specificity_records]
    db.bulk_save_objects(db_records)
    db.flush()


def bulk_create_tissue_complexity(
        db: Session,
        tissue_complexity_records: list):
    db_records = [
        models.TissueComplexity(
            **record.dict()) for record in tissue_complexity_records]
    db.bulk_save_objects(db_records)
    db.flush()
