from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/metadata",
    tags=["metadata"],
)


@router.get("/", response_model=List[schemas.Metadata])
def read_metadata(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)):
    metadata = crud.get_all_metadata(db, skip=skip, limit=limit)
    return metadata


@router.get("/{metadata_id}", response_model=schemas.Metadata)
def read_metadata_by_id(metadata_id: int, db: Session = Depends(get_db)):
    db_metadata = crud.get_metadata(db, metadata_id=metadata_id)
    if db_metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return db_metadata


@router.post("/", response_model=schemas.Metadata)
def create_metadata(
        metadata: schemas.MetadataCreate,
        db: Session = Depends(get_db)):
    return crud.create_metadata(db=db, metadata=metadata)


@router.put("/{metadata_id}", response_model=schemas.Metadata)
def update_metadata(
        metadata_id: int,
        metadata: schemas.MetadataCreate,
        db: Session = Depends(get_db)):
    db_metadata = crud.update_metadata(
        db, metadata_id=metadata_id, metadata=metadata)
    if db_metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return db_metadata


@router.delete("/{metadata_id}", response_model=schemas.Metadata)
def delete_metadata(metadata_id: int, db: Session = Depends(get_db)):
    db_metadata = crud.delete_metadata(db, metadata_id=metadata_id)
    if db_metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return db_metadata
