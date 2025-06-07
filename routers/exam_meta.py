from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import String
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

            # round_subjects with joined subject and start_no
            round_subjects = (
                db.query(
                    RoundSubject,
                    Subject.subject_code,
                    Subject.subject_name,
                    func.min(Question.question_no).label("start_no")
                )
                .join(Subject, Subject.id == RoundSubject.subject_id)
                .join(Question, Question.round_subject_id == RoundSubject.id)
                .filter(RoundSubject.exam_round_id == round.id)
                .group_by(RoundSubject.id, Subject.subject_code, Subject.subject_name, RoundSubject.session)
                .all()
            )

            for rs, subject_code, subject_name, start_no in round_subjects:
                session_str = str(rs.session)
                if session_str not in meta[year_str][round_str]:
                    meta[year_str][round_str][session_str] = []

                meta[year_str][round_str][session_str].append({
                    "subject_code": subject_code,
                    "subject_name": subject_name,
                    "start_no": start_no
                })

        exam_meta_map[exam.exam_code] = {
            "exam_name": exam.exam_name,
            "meta": meta
        }

        print(f"exam_meta_map:{exam_meta_map}")

    return { "exam_meta_map": exam_meta_map }
