from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.exam_model import Exam
from schemas.exam_schema import ExamCreate, ExamUpdate, ExamResponse
from typing import List

router = APIRouter(
    prefix="/admin/exam",
    tags=["Admin Exam"]
)

@router.get("", response_model=List[ExamResponse])
def get_exams(db: Session = Depends(get_db)):
    return db.query(Exam).order_by(Exam.exam_code.asc()).all()

@router.post("", response_model=ExamResponse)
def create_exam(data: ExamCreate, db: Session = Depends(get_db)):
    exam = Exam(**data.dict())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam

@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(exam_id: int, data: ExamUpdate, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="자격증이 존재하지 않습니다.")
    for key, value in data.dict().items():
        setattr(exam, key, value)
    db.commit()
    db.refresh(exam)
    return exam

@router.delete("/{exam_id}", status_code=204)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="자격증이 존재하지 않습니다.")
    db.delete(exam)
    db.commit()
