from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/samples",
    tags=["samples"],
)


@router.get("/", response_model=List[schemas.Sample])
def read_samples(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)):
    samples = crud.get_samples(db, skip=skip, limit=limit)
    return samples


@router.get("/{sample_id}", response_model=schemas.Sample)
def read_sample(sample_id: str, db: Session = Depends(get_db)):
    db_sample = crud.get_sample(db, sample_id=sample_id)
    if db_sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    return db_sample


@router.post("/", response_model=schemas.Sample)
def create_sample(sample: schemas.SampleCreate, db: Session = Depends(get_db)):
    return crud.create_sample(db=db, sample=sample)


@router.put("/{sample_id}", response_model=schemas.Sample)
def update_sample(
        sample_id: str,
        sample: schemas.SampleCreate,
        db: Session = Depends(get_db)):
    db_sample = crud.update_sample(db, sample_id=sample_id, sample=sample)
    if db_sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    return db_sample


@router.delete("/{sample_id}", response_model=schemas.Sample)
def delete_sample(sample_id: str, db: Session = Depends(get_db)):
    db_sample = crud.delete_sample(db, sample_id=sample_id)
    if db_sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    return db_sample
