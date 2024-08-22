from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/tissue_specificities",
    tags=["tissue_specificities"],
)


@router.get("/", response_model=List[schemas.TissueSpecificity])
def read_tissue_specificities(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)):
    tissue_specificities = crud.get_tissue_specificities(
        db, skip=skip, limit=limit)
    return tissue_specificities


@router.get("/{tissue_specificity_id}",
            response_model=schemas.TissueSpecificity)
def read_tissue_specificity(
        tissue_specificity_id: int,
        db: Session = Depends(get_db)):
    db_tissue_specificity = crud.get_tissue_specificity(
        db, tissue_specificity_id=tissue_specificity_id)
    if db_tissue_specificity is None:
        raise HTTPException(
            status_code=404,
            detail="Tissue specificity not found")
    return db_tissue_specificity


@router.post("/", response_model=schemas.TissueSpecificity)
def create_tissue_specificity(
        tissue_specificity: schemas.TissueSpecificityCreate,
        db: Session = Depends(get_db)):
    return crud.create_tissue_specificity(
        db=db, tissue_specificity=tissue_specificity)


@router.put("/{tissue_specificity_id}",
            response_model=schemas.TissueSpecificity)
def update_tissue_specificity(
        tissue_specificity_id: int,
        tissue_specificity: schemas.TissueSpecificityCreate,
        db: Session = Depends(get_db)):
    db_tissue_specificity = crud.update_tissue_specificity(
        db,
        tissue_specificity_id=tissue_specificity_id,
        tissue_specificity=tissue_specificity)
    if db_tissue_specificity is None:
        raise HTTPException(
            status_code=404,
            detail="Tissue specificity not found")
    return db_tissue_specificity


@router.delete("/{tissue_specificity_id}",
               response_model=schemas.TissueSpecificity)
def delete_tissue_specificity(
        tissue_specificity_id: int,
        db: Session = Depends(get_db)):
    db_tissue_specificity = crud.delete_tissue_specificity(
        db, tissue_specificity_id=tissue_specificity_id)
    if db_tissue_specificity is None:
        raise HTTPException(
            status_code=404,
            detail="Tissue specificity not found")
    return db_tissue_specificity
