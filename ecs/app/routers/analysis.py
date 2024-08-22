from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/analyses",
    tags=["analyses"],
)


@router.get("/", response_model=List[schemas.Analysis])
def read_analyses(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)):
    analyses = crud.get_analyses(db, skip=skip, limit=limit)
    return analyses


@router.get("/analyses/session/{session_id}",
            response_model=List[schemas.Analysis])
def get_analyses_by_session_id(
        session_id: str,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user)):
    return crud.get_analyses_by_session_id(db, session_id=session_id)


@router.get("/{analysis_id}", response_model=schemas.Analysis)
def read_analysis(analysis_id: int, db: Session = Depends(get_db)):
    db_analysis = crud.get_analysis(db, analysis_id=analysis_id)
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return db_analysis


@router.post("/", response_model=schemas.Analysis)
def create_analysis(
        analysis: schemas.AnalysisCreate,
        db: Session = Depends(get_db)):
    return crud.create_analysis(db=db, analysis=analysis)


@router.put("/{analysis_id}", response_model=schemas.Analysis)
def update_analysis(
        analysis_id: int,
        analysis: schemas.AnalysisCreate,
        db: Session = Depends(get_db)):
    db_analysis = crud.update_analysis(
        db, analysis_id=analysis_id, analysis=analysis)
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return db_analysis


@router.delete("/{analysis_id}", response_model=schemas.Analysis)
def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    db_analysis = crud.delete_analysis(db, analysis_id=analysis_id)
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return db_analysis
