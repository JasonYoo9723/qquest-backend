from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.round_subject_model import RoundSubject
from schemas.round_subject_schema import (
    RoundSubjectCreate,
    RoundSubjectUpdate,
    RoundSubjectOut
)
from database import get_db

router = APIRouter(prefix="/admin/round-subject", tags=["Admin - RoundSubject"])

@router.get("", response_model=list[RoundSubjectOut])
def list_round_subjects(db: Session = Depends(get_db)):
    return db.query(RoundSubject).order_by(RoundSubject.exam_round_id.asc(), RoundSubject.subject_id.asc()).all()

@router.post("", response_model=RoundSubjectOut)
def create_round_subject(payload: RoundSubjectCreate, db: Session = Depends(get_db)):
    new_rs = RoundSubject(**payload.dict())
    db.add(new_rs)
    db.commit()
    db.refresh(new_rs)
    return new_rs

@router.put("/{rs_id}", response_model=RoundSubjectOut)
def update_round_subject(rs_id: int, payload: RoundSubjectUpdate, db: Session = Depends(get_db)):
    rs = db.query(RoundSubject).filter(RoundSubject.id == rs_id).first()
    if not rs:
        raise HTTPException(status_code=404, detail="RoundSubject not found")
    for k, v in payload.dict().items():
        setattr(rs, k, v)
    db.commit()
    db.refresh(rs)
    return rs

@router.delete("/{rs_id}")
def delete_round_subject(rs_id: int, db: Session = Depends(get_db)):
    rs = db.query(RoundSubject).filter(RoundSubject.id == rs_id).first()
    if not rs:
        raise HTTPException(status_code=404, detail="RoundSubject not found")
    db.delete(rs)
    db.commit()
    return {"ok": True}
