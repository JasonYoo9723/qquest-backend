from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.subject_model import Subject
from schemas.subject_schema import SubjectCreate, SubjectUpdate, SubjectOut
from database import get_db

router = APIRouter(prefix="/admin/subject", tags=["Admin - Subject"])

@router.get("", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).order_by(Subject.subject_code.asc()).all()

@router.post("", response_model=SubjectOut)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    new_subject = Subject(**payload.dict())
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject

@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, payload: SubjectUpdate, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    for k, v in payload.dict().items():
        setattr(subject, k, v)
    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()
    return {"ok": True}

@router.get("/by-exam/{exam_id}", response_model=list[SubjectOut])
def list_subjects_by_exam(exam_id: int, db: Session = Depends(get_db)):
    return db.query(Subject).filter(Subject.exam_id == exam_id).order_by(Subject.subject_name).all()

