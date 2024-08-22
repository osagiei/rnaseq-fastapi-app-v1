from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/gene_expressions",
    tags=["gene_expressions"],
)


@router.get("/", response_model=List[schemas.GeneExpression])
def read_gene_expressions(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)):
    gene_expressions = crud.get_gene_expressions(db, skip=skip, limit=limit)
    return gene_expressions


@router.get("/{gene_expression_id}", response_model=schemas.GeneExpression)
def read_gene_expression(
        gene_expression_id: int,
        db: Session = Depends(get_db)):
    db_gene_expression = crud.get_gene_expression(
        db, gene_expression_id=gene_expression_id)
    if db_gene_expression is None:
        raise HTTPException(
            status_code=404,
            detail="Gene expression not found")
    return db_gene_expression


@router.post("/", response_model=schemas.GeneExpression)
def create_gene_expression(
        gene_expression: schemas.GeneExpressionCreate,
        db: Session = Depends(get_db)):
    return crud.create_gene_expression(db=db, gene_expression=gene_expression)


@router.put("/{gene_expression_id}", response_model=schemas.GeneExpression)
def update_gene_expression(
        gene_expression_id: int,
        gene_expression: schemas.GeneExpressionCreate,
        db: Session = Depends(get_db)):
    db_gene_expression = crud.update_gene_expression(
        db, gene_expression_id=gene_expression_id, gene_expression=gene_expression)
    if db_gene_expression is None:
        raise HTTPException(
            status_code=404,
            detail="Gene expression not found")
    return db_gene_expression


@router.delete("/{gene_expression_id}", response_model=schemas.GeneExpression)
def delete_gene_expression(
        gene_expression_id: int,
        db: Session = Depends(get_db)):
    db_gene_expression = crud.delete_gene_expression(
        db, gene_expression_id=gene_expression_id)
    if db_gene_expression is None:
        raise HTTPException(
            status_code=404,
            detail="Gene expression not found")
    return db_gene_expression
