# routers\public\question.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from database import get_db
from models.exam_model import Exam
from models.exam_round_model import ExamRound
from models.round_subject_model import RoundSubject
from models.subject_model import Subject
from models.question_model import Question
from models.choice_model import Choice
from models.answer_model import Answer
from models.exam_result_model import ExamResult
from models.exam_wrong_question_model import ExamWrongQuestion
from schemas.question_schema import UploadRequest, SubjectResponse, StartExamRequest, ExamFilterRequest, ExamResultOut, ExamResultCreate, ExamWrongQuestionDetailed

from typing import List
from pydantic import BaseModel
from typing import Optional

from dependencies.auth import get_current_user
from models.user_model import User

router = APIRouter()

@router.get("/exams")
def get_exams(db: Session = Depends(get_db)):
    exams = db.query(Exam.exam_code, Exam.exam_name).distinct().all()
    return {"exams": [{"exam_code": e.exam_code, "exam_name": e.exam_name} for e in exams]}


@router.get("/exam-metadata")
def get_exam_metadata(
    exam_code: str,
    session: int = 1,
    db: Session = Depends(get_db)
):
    exam = db.query(Exam).filter(Exam.exam_code == exam_code).first()
    if not exam:
        raise HTTPException(status_code=404, detail="시험 정보 없음")

    rounds = db.query(ExamRound).filter(ExamRound.exam_id == exam.id).all()
    years = sorted({r.year for r in rounds}, reverse=True)

    session_rows = (
        db.query(RoundSubject.session)
        .join(ExamRound)
        .filter(ExamRound.exam_id == exam.id)
        .filter(RoundSubject.session.isnot(None))
        .distinct()
        .order_by(RoundSubject.session)
        .all()
    )
    sessions = [str(row.session) for row in session_rows]

    # 과목 + 시작문제번호
    subject_rows = (
        db.query(
            Subject.subject_code,
            Subject.subject_name,
            RoundSubject.session,
            func.min(Question.question_no).label("start_no")
        )
        .join(RoundSubject, RoundSubject.subject_id == Subject.id)
        .join(ExamRound, RoundSubject.exam_round_id == ExamRound.id)
        .join(Question, Question.round_subject_id == RoundSubject.id)
        .filter(ExamRound.exam_id == exam.id)
        .group_by(Subject.subject_code, Subject.subject_name, RoundSubject.session)
        .all()
    )

    subjects = [
        {
            "subject_code": s.subject_code,
            "subject_name": s.subject_name,
            "session": str(s.session),
            "start_no": s.start_no
        } for s in subject_rows
    ]

    return {
        "years": years,
        "sessions": sessions,
        "subjects": subjects
    }

@router.get("/learn/random-question")
def get_random_question(
    exam_code: str,
    year: Optional[int] = None,
    round: Optional[int] = None,
    session: Optional[int] = None,
    subject: Optional[str] = None,
    mode: str = "RAN",
    question_no: int = 1,
    db: Session = Depends(get_db)
):
    query = db.query(Question)\
        .join(RoundSubject)\
        .join(ExamRound)\
        .join(Exam)\
        .join(Subject)

    # 필터 조건: 전체 선택 시(None), 해당 조건 생략
    query = query.filter(Exam.exam_code == exam_code)
    if year is not None:
        query = query.filter(ExamRound.year == year)
    if round is not None:
        query = query.filter(ExamRound.round == round)
    if session is not None:
        query = query.filter(RoundSubject.session == session)
    if subject is not None:
        query = query.filter(Subject.subject_code == subject)

    if mode == "RAN":
        query = query.order_by(func.random())
    else:
        query = query.filter(Question.question_no == question_no).order_by(Question.question_no)

    question = query.first()
    if not question:
        raise HTTPException(status_code=404, detail="문제가 없습니다.")

    answer_row = db.query(Answer).filter_by(question_id=question.id).first()
    answer_number = answer_row.choice_number if answer_row else None

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
        "answer": answer_number
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
                .filter_by(exam_round_id=exam_round.id, subject_id=subject.id, session=payload.session)
                .first()
            )
            if not round_subject:
                round_subject = RoundSubject(
                    exam_round_id=exam_round.id,
                    subject_id=subject.id,
                    session=payload.session
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


class ExamInfoResponse(BaseModel):
    exam_code: str
    exam_name: str

@router.get("/exams/info", response_model=ExamInfoResponse)
def get_exam_info(exam_code: str, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter_by(exam_code=exam_code).first()
    if not exam:
        raise HTTPException(status_code=404, detail="해당 시험 코드가 존재하지 않습니다.")
    return ExamInfoResponse(exam_code=exam.exam_code, exam_name=exam.exam_name)

@router.post("/exam/start")
def start_exam(
    req: StartExamRequest,
    db: Session = Depends(get_db)
):
    query = (
        db.query(Question, Exam, Subject, ExamRound)
        .join(RoundSubject, Question.round_subject_id == RoundSubject.id)
        .join(ExamRound, RoundSubject.exam_round_id == ExamRound.id)
        .join(Exam, ExamRound.exam_id == Exam.id)
        .join(Subject, RoundSubject.subject_id == Subject.id)
    )

    if req.exam_code:
        query = query.filter(Exam.exam_code == req.exam_code)
    if req.year:
        query = query.filter(ExamRound.year == req.year)
    if req.round:
        query = query.filter(ExamRound.round == req.round)
    if req.session:
        query = query.filter(RoundSubject.session == req.session)
    if req.subject:
        query = query.filter(Subject.subject_code == req.subject)

    rows = query.order_by(func.random()).limit(req.count).all()

    results = []
    for q, exam, subject, exam_round in rows:
        results.append({
            "id": q.id,
            "question_no": q.question_no,
            "question_text": q.question_text,
            "choices": [
                {
                    "number": c.choice_number,
                    "content": c.choice_content
                } for c in sorted(q.choices, key=lambda x: x.choice_number)
            ],
            "exam_name": exam.exam_name,
            "subject_name": subject.subject_name,
            "year": exam_round.year,
            "round": exam_round.round,
            "answer": q.answer.choice_number if q.answer else None
        })

    return results


@router.post("/exam/count")
def count_questions(
    req: ExamFilterRequest,
    db: Session = Depends(get_db)
):
    query = db.query(Question).join(RoundSubject).join(ExamRound).join(Exam).join(Subject)

    if req.exam_code:
        query = query.filter(Exam.exam_code == req.exam_code)
    if req.year:
        query = query.filter(ExamRound.year == req.year)
    if req.round:
        query = query.filter(ExamRound.round == req.round)
    if req.session:
        query = query.filter(RoundSubject.session == req.session)
    if req.subject:
        query = query.filter(Subject.subject_code == req.subject)

    count = query.count()
    return {"count": count}

@router.get("/exam/result/{result_id}", response_model=ExamResultOut)
def get_exam_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.query(ExamResult).filter(
        ExamResult.id == result_id,
        ExamResult.user_id == current_user.id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="시험 결과를 찾을 수 없습니다.")

    # 오답 상세 조회
    wrongs = (
        db.query(ExamWrongQuestion)
        .filter(ExamWrongQuestion.result_id == result.id)
        .all()
    )

    wrong_questions_detailed = []

    for w in wrongs:
        question = db.query(Question).filter(Question.id == w.question_id).first()
        choices = (
            db.query(Choice)
            .filter(Choice.question_id == question.id)
            .order_by(Choice.choice_number)
            .all()
        )

        wrong_questions_detailed.append({
            "question_id": question.id,
            "question_no": question.question_no,
            "question_text": question.question_text,
            "choices": [c.choice_content for c in choices],
            "chosen_choice": w.chosen_choice,
            "correct_choice": question.answer.choice_number if question.answer else None
        })

    return {
        "id": result.id,
        "exam_code": result.exam_code,
        "exam_name": result.exam.exam_name if result.exam else result.exam_code,
        "subject": result.subject,
        "subject_name": result.subject_obj.subject_name if result.subject_obj else result.subject,
        "year": result.year,
        "round": result.round,
        "session": result.session,
        "total_count": result.total_count,
        "correct_count": result.correct_count,
        "wrong_count": result.wrong_count,
        "duration_seconds": result.duration_seconds,
        "taken_at": result.taken_at,
        "wrong_questions": wrong_questions_detailed
    }


@router.post("/exam/finish", response_model=ExamResultOut)
def finish_exam(
    data: ExamResultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = ExamResult(
        user_id=current_user.id,
        exam_code=data.exam_code,
        year=data.year,
        round=data.round,
        session=data.session,
        subject=data.subject,
        total_count=data.total_count,
        correct_count=data.correct_count,
        wrong_count=data.wrong_count,
        duration_seconds=data.duration_seconds
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    for wq in data.wrong_questions:
        wrong = ExamWrongQuestion(
            result_id=result.id,
            question_id=wq.question_id,
            chosen_choice=wq.chosen_choice
        )
        db.add(wrong)
    db.commit()

    # 오답 상세 데이터 조회
    wrongs = db.query(ExamWrongQuestion).filter_by(result_id=result.id).all()
    wrong_questions_detailed = []

    for w in wrongs:
        question = db.query(Question).filter(Question.id == w.question_id).first()
        choices = db.query(Choice).filter(Choice.question_id == w.question_id).order_by(Choice.choice_number).all()
        answer_row = db.query(Answer).filter_by(question_id=question.id).first()
        correct_choice = answer_row.choice_number if answer_row else None

        wrong_questions_detailed.append(ExamWrongQuestionDetailed(
            question_id=question.id,
            question_no=question.question_no,
            question_text=question.question_text,
            choices=[c.choice_content for c in choices],
            chosen_choice=w.chosen_choice,
            correct_choice=correct_choice
        ))

    return ExamResultOut(
        id=result.id,
        exam_code=result.exam_code,
        exam_name=result.exam.exam_name if result.exam else result.exam_code,
        subject=result.subject,
        subject_name=result.subject_obj.subject_name if result.subject_obj else result.subject,
        year=result.year,
        round=result.round,
        session=result.session,
        total_count=result.total_count,
        correct_count=result.correct_count,
        wrong_count=result.wrong_count,
        duration_seconds=result.duration_seconds,
        taken_at=result.taken_at,
        wrong_questions=wrong_questions_detailed
    )

@router.get("/exam/history")
def get_exam_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = (
        db.query(ExamResult)
        .filter(ExamResult.user_id == user.id)
        .order_by(ExamResult.taken_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "exam_name": r.exam.exam_name,
            "year": r.year,
            "round": r.round,
            "session": r.session,
            "total": r.total_count,
            "correct": r.correct_count,
            "wrong": r.wrong_count,
            "created_at": r.taken_at.isoformat(),
        }
        for r in results
    ]