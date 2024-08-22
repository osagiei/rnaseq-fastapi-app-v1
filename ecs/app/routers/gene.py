from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/genes",
    tags=["genes"],
)


@router.get("/", response_model=List[schemas.Gene])
def read_genes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    genes = crud.get_genes(db, skip=skip, limit=limit)
    return genes


@router.get("/{coord_id}", response_model=schemas.Gene)
def read_gene(coord_id: str, db: Session = Depends(get_db)):
    db_gene = crud.get_gene(db, coord_id=coord_id)
    if db_gene is None:
        raise HTTPException(status_code=404, detail="Gene not found")
    return db_gene


@router.post("/", response_model=schemas.Gene)
def create_gene(gene: schemas.GeneCreate, db: Session = Depends(get_db)):
    return crud.create_gene(db=db, gene=gene)


@router.put("/{coord_id}", response_model=schemas.Gene)
def update_gene(
        coord_id: str,
        gene: schemas.GeneCreate,
        db: Session = Depends(get_db)):
    db_gene = crud.update_gene(db, coord_id=coord_id, gene=gene)
    if db_gene is None:
        raise HTTPException(status_code=404, detail="Gene not found")
    return db_gene


@router.delete("/{coord_id}", response_model=schemas.Gene)
def delete_gene(coord_id: str, db: Session = Depends(get_db)):
    db_gene = crud.delete_gene(db, coord_id=coord_id)
    if db_gene is None:
        raise HTTPException(status_code=404, detail="Gene not found")
    return db_gene
