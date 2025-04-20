from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from database import get_db
from models.exam_model import Exam, Subject, ExamRound, RoundSubject, Question, Choice
from schemas import UploadRequest

import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🔥 에러 발생:", repr(exc), file=sys.stderr, flush=True)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("💥 요청 유효성 검사 실패:", exc, file=sys.stderr, flush=True)
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "body": exc.body})


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
    subject_names = db.query(Subject.subject_name).filter(Subject.id.in_(subject_ids)).all()

    return {
        "years": years,
        "subjects": [s[0] for s in subject_names]
    }


@router.get("/learn/random-question")
def get_random_question(exam_code: str = "", db: Session = Depends(get_db)):
    query = db.query(Question).join(RoundSubject).join(ExamRound).join(Exam)
    if exam_code:
        query = query.filter(Exam.exam_code == exam_code)

    question = query.order_by(func.random()).first()
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
    print("🔥 save_questions 진입", file=sys.stderr, flush=True)

    try:
        # 1. 자격증 마스터에서 exam_id 조회
        exam = db.query(Exam).filter(Exam.exam_code == payload.exam_code).first()
        if not exam:
            raise HTTPException(status_code=400, detail=f"존재하지 않는 exam_code: {payload.exam_code}")

        # 2. 회차 존재 여부 확인, 없으면 생성
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
            db.flush()  # exam_round.id 확보

        subject_map = {}

        for q in payload.questions:
            subject_name = q.subject_name.strip()

            # 3. 과목 마스터에서 subject_id 조회
            if subject_name in subject_map:
                subject = subject_map[subject_name]
            else:
                subject = db.query(Subject).filter(Subject.subject_name == subject_name).first()
                if not subject:
                    raise HTTPException(status_code=400, detail=f"존재하지 않는 과목: {subject_name}")
                subject_map[subject_name] = subject

            # 4. 회차-과목 연결 (없으면 생성)
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
                db.flush()  # round_subject.id 확보

            # 5. 문제 저장
            question = Question(
                round_subject_id=round_subject.id,
                question_no=q.question_no,
                question_text=q.question_text,
            )
            db.add(question)
            db.flush()  # question.id 확보

            # 6. 보기 저장
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
        print("🔥 저장 중 오류:", repr(e), file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


app.include_router(router)
