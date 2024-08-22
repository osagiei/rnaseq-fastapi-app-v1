from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/tissue_complexities",
    tags=["tissue_complexities"],
)


@router.get("/", response_model=List[schemas.TissueComplexity])
def read_tissue_complexities(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)):
    tissue_complexities = crud.get_tissue_complexities(
        db, skip=skip, limit=limit)
    return tissue_complexities


@router.get("/{tissue_complexity_id}", response_model=schemas.TissueComplexity)
def read_tissue_complexity(
        tissue_complexity_id: int,
        db: Session = Depends(get_db)):
    db_tissue_complexity = crud.get_tissue_complexity(
        db, tissue_complexity_id=tissue_complexity_id)
    if db_tissue_complexity is None:
        raise HTTPException(
            status_code=404,
            detail="Tissue complexity not found")
    return db_tissue_complexity


@router.post("/", response_model=schemas.TissueComplexity)
def create_tissue_complexity(
        tissue_complexity: schemas.TissueComplexityCreate,
        db: Session = Depends(get_db)):
    return crud.create_tissue_complexity(
        db=db, tissue_complexity=tissue_complexity)


@router.put("/{tissue_complexity_id}", response_model=schemas.TissueComplexity)
def update_tissue_complexity(
        tissue_complexity_id: int,
        tissue_complexity: schemas.TissueComplexityCreate,
        db: Session = Depends(get_db)):
    db_tissue_complexity = crud.update_tissue_complexity(
        db,
        tissue_complexity_id=tissue_complexity_id,
        tissue_complexity=tissue_complexity)
    if db_tissue_complexity is None:
        raise HTTPException(
            status_code=404,
            detail="Tissue complexity not found")
    return db_tissue_complexity


@router.delete("/{tissue_complexity_id}",
               response_model=schemas.TissueComplexity)
def delete_tissue_complexity(
        tissue_complexity_id: int,
        db: Session = Depends(get_db)):
    db_tissue_complexity = crud.delete_tissue_complexity(
        db, tissue_complexity_id=tissue_complexity_id)
    if db_tissue_complexity is None:
        raise HTTPException(
            status_code=404,
            detail="Tissue complexity not found")
    return db_tissue_complexity
