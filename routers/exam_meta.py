from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, select
from database import get_db
from models.exam_model import Exam, ExamRound, RoundSubject, Subject, Question

router = APIRouter()

@router.get("/exam-meta-map")
def get_exam_meta_map(db: Session = Depends(get_db)):
    exams = db.query(Exam).all()
    exam_meta_map = {}

    for exam in exams:
        meta = {}

        exam_rounds = db.query(ExamRound).filter(ExamRound.exam_id == exam.id).all()
        for round in exam_rounds:
            year_str = str(round.year)
            round_str = str(round.round)

            if year_str not in meta:
                meta[year_str] = {}
            if round_str not in meta[year_str]:
                meta[year_str][round_str] = {}

            # ✅ 먼저 RoundSubject + Subject 가져오기
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

                # ✅ optional start_no (있으면 포함)
                start_no = db.query(func.min(Question.question_no)).filter(
                    Question.round_subject_id == rs_id
                ).scalar()

                entry = {
                    "subject_name": subject_name
                }
                if start_no is not None:
                    entry["start_no"] = start_no

                meta[year_str][round_str][session_str][subject_code] = entry

        exam_meta_map[exam.exam_code] = {
            "exam_name": exam.exam_name,
            "meta": meta
        }

    return {"exam_meta_map": exam_meta_map}
