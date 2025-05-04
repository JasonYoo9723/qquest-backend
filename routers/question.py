### 📄 파일: routers/question.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from database import get_db
from models.exam_model import Exam, ExamRound, RoundSubject, Subject, Question, Choice
from schemas.question_schema import UploadRequest

router = APIRouter()

@router.get("/exams")
def get_exams(db: Session = Depends(get_db)):
    exams = db.query(Exam.exam_code, Exam.exam_name).distinct().all()
    return {"exams": [{"exam_code": e.exam_code, "exam_name": e.exam_name} for e in exams]}


@router.get("/exam-metadata")
def get_exam_metadata(exam_code: str, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.exam_code == exam_code).first()
    if not exam:
        raise HTTPException(status_code=404, detail="시험 정보 없음")

    rounds = db.query(ExamRound).filter(ExamRound.exam_id == exam.id).all()
    years = sorted({r.year for r in rounds}, reverse=True)

    subject_ids = db.query(RoundSubject.subject_id).join(ExamRound).filter(ExamRound.exam_id == exam.id).distinct()
    subjects = db.query(Subject.subject_code, Subject.subject_name).filter(Subject.id.in_(subject_ids)).all()

    return {
        "years": years,
        "subjects": [
            {"subject_code": s.subject_code, "subject_name": s.subject_name} for s in subjects
        ]
    }


@router.get("/learn/random-question")
def get_random_question(
    exam_code: str = "",
    year: int = 0,
    subject: str = "",
    mode: str = "RAN",
    question_no: int = 1,
    db: Session = Depends(get_db)
):
    query = db.query(Question).join(RoundSubject).join(ExamRound).join(Exam).join(Subject)

    if exam_code:
        query = query.filter(Exam.exam_code == exam_code)
    if year:
        query = query.filter(ExamRound.year == year)
    if subject:
        query = query.filter(Subject.subject_code == subject)

    if mode == "RAN":
        query = query.order_by(func.random())
    else:
        query = query.order_by(Question.question_no.asc()).filter(Question.question_no == question_no)

    question = query.first()
    if not question:
        raise HTTPException(status_code=404, detail="문제가 없습니다.")

    return {
        "id": question.id,
        "question_no": question.question_no,
        "question_text": question.question_text,
        "subject_name": question.round_subject.subject.subject_name,
        "exam_name": question.round_subject.exam_round.exam.exam_name,
        "year": question.round_subject.exam_round.year,
        "round": question.round_subject.exam_round.round,
        "choices": [
            {
                "number": c.choice_number,
                "content": c.choice_content
            } for c in sorted(question.choices, key=lambda x: x.choice_number)
        ],
        "answer": question.question_answer
    }


@router.post("/admin/save-questions")
def save_questions(payload: UploadRequest, db: Session = Depends(get_db)):
    try:
        exam = db.query(Exam).filter(Exam.exam_code == payload.exam_code).first()
        if not exam:
            raise HTTPException(status_code=400, detail=f"존재하지 않는 exam_code: {payload.exam_code}")

        exam_round = (
            db.query(ExamRound)
            .filter_by(exam_id=exam.id, year=payload.year, round=payload.round)
            .first()
        )
        if not exam_round:
            exam_round = ExamRound(
                exam_id=exam.id,
                year=payload.year,
                round=payload.round
            )
            db.add(exam_round)
            db.flush()

        subject_map = {}

        for q in payload.questions:
            subject_code = q.subject_code.strip()
            if subject_code in subject_map:
                subject = subject_map[subject_code]
            else:
                subject = db.query(Subject).filter(Subject.subject_code == subject_code).first()
                if not subject:
                    raise HTTPException(status_code=400, detail=f"존재하지 않는 과목코드: {subject_code}")
                subject_map[subject_code] = subject

            round_subject = (
                db.query(RoundSubject)
                .filter_by(exam_round_id=exam_round.id, subject_id=subject.id)
                .first()
            )
            if not round_subject:
                round_subject = RoundSubject(
                    exam_round_id=exam_round.id,
                    subject_id=subject.id
                )
                db.add(round_subject)
                db.flush()

            question = Question(
                round_subject_id=round_subject.id,
                question_no=q.question_no,
                question_text=q.question_text,
                question_answer=q.question_answer
            )
            db.add(question)
            db.flush()

            for idx, choice in enumerate(q.choices):
                db.add(Choice(
                    question_id=question.id,
                    choice_number=idx + 1,
                    choice_content=choice.choice_content
                ))

        db.commit()
        return {"message": "저장 완료"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
