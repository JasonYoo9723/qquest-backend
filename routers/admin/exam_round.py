from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.exam_round_model import ExamRound
from schemas.exam_round_schema import ExamRoundCreate, ExamRoundUpdate, ExamRoundOut
from database import get_db

router = APIRouter(prefix="/admin/exam-round", tags=["Admin - ExamRound"])

@router.get("", response_model=list[ExamRoundOut])
def list_exam_rounds(db: Session = Depends(get_db)):
    return db.query(ExamRound).order_by(ExamRound.exam_id.asc()).all()

@router.post("", response_model=ExamRoundOut)
def create_exam_round(payload: ExamRoundCreate, db: Session = Depends(get_db)):
    new_round = ExamRound(**payload.dict())
    db.add(new_round)
    db.commit()
    db.refresh(new_round)
    return new_round

@router.put("/{round_id}", response_model=ExamRoundOut)
def update_exam_round(round_id: int, payload: ExamRoundUpdate, db: Session = Depends(get_db)):
    round_obj = db.query(ExamRound).filter(ExamRound.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Exam round not found")
    for k, v in payload.dict().items():
        setattr(round_obj, k, v)
    db.commit()
    db.refresh(round_obj)
    return round_obj

@router.delete("/{round_id}")
def delete_exam_round(round_id: int, db: Session = Depends(get_db)):
    round_obj = db.query(ExamRound).filter(ExamRound.id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Exam round not found")
    db.delete(round_obj)
    db.commit()
    return {"ok": True}
