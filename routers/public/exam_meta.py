from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db

from models.exam_model import Exam
from models.exam_round_model import ExamRound
from models.round_subject_model import RoundSubject
from models.subject_model import Subject
from models.question_model import Question

router = APIRouter(
    prefix="/public/exam-meta",
    tags=["Public Exam Meta"]
)


@router.get("/map")
def get_exam_meta_map(db: Session = Depends(get_db)):
    exams = db.query(Exam).all()
    exam_meta_map = {}

    for exam in exams:
        meta = {}
        exam_rounds = db.query(ExamRound).filter_by(exam_id=exam.id).all()

        for round in exam_rounds:
            year_str = str(round.year)
            round_str = str(round.round)

            if year_str not in meta:
                meta[year_str] = {}
            if round_str not in meta[year_str]:
                meta[year_str][round_str] = {}

            round_subjects = (
                db.query(
                    RoundSubject.id,
                    RoundSubject.session,
                    Subject.subject_code,
                    Subject.subject_name
                )
                .join(Subject, Subject.id == RoundSubject.subject_id)
                .filter(RoundSubject.exam_round_id == round.id)
                .all()
            )

            for rs_id, session, subject_code, subject_name in round_subjects:
                session_str = str(session)
                if session_str not in meta[year_str][round_str]:
                    meta[year_str][round_str][session_str] = {}

                start_no = (
                    db.query(func.min(Question.question_no))
                    .filter(Question.round_subject_id == rs_id)
                    .scalar()
                )

                entry = {"subject_name": subject_name}
                if start_no is not None:
                    entry["start_no"] = start_no

                meta[year_str][round_str][session_str][subject_code] = entry

        exam_meta_map[exam.exam_code] = {
            "exam_name": exam.exam_name,
            "meta": meta
        }

    return {"exam_meta_map": exam_meta_map}
