from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.routers import auth, gene, gene_expression, metadata, analysis, sample, tissue_specificity, tissue_complexity, utils, landing
from app.database import SessionLocal, engine
from app.models import Gene, Base
from app.utils.gtf_loader import parse_and_load_gtf
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, Depends
from app.database import get_db, init_db
from app.routers.auth import get_current_user
import os
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(gene.router)
app.include_router(gene_expression.router)
app.include_router(analysis.router)
app.include_router(sample.router)
app.include_router(tissue_specificity.router)
app.include_router(tissue_complexity.router)
app.include_router(utils.router)
app.include_router(metadata.router)
app.include_router(auth.router)
app.include_router(landing.router)


@app.on_event("startup")
async def startup_event():
    init_db()
    db: Session = SessionLocal()

    gene_count = db.query(Gene).count()
    if gene_count == 0:
        print("Gene table is empty. Loading data from GTF...")
        parse_and_load_gtf(
            DBUSER=os.getenv('DBUSER'),
            DBPASSWORD=os.getenv('DBPASSWORD'),
            DBHOST=os.getenv('DBHOST'),
            DBPORT=os.getenv('DBPORT'),
            DBNAME=os.getenv('DBNAME'),
            gtf_url="https://ftp.ensembl.org/pub/release-112/gtf/mus_musculus/Mus_musculus.GRCm39.112.gtf.gz"
        )
    else:
        print(f"Gene table already has {gene_count} records.")

    db.close()


app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/landing")
def landing_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return templates.TemplateResponse(
        "landing.html", {
            "request": request, "user": user})
