from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.gtf_loader import parse_and_load_gtf

router = APIRouter(
    prefix="/utils",
    tags=["utils"],
)


@router.post("/load_gtf/")
def load_gtf(
        background_tasks: BackgroundTasks,
        gtf_url: str,
        db: Session = Depends(get_db)):
    background_tasks.add_task(
        parse_and_load_gtf,
        'root',
        'nakwoshi',
        'localhost',
        3306,
        'rnaseq_db',
        gtf_url)
    return {"message": "GTF loading started in the background"}
