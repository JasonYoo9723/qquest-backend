# routers\admin_modify.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.exam_model import Exam, ExamRound, RoundSubject, Subject, Question, Choice, Answer
from schemas.question_schema import UpdateQuestionRequest, QuestionUpdateItem

router = APIRouter()

@router.get("/admin/get-questions")
def get_questions(exam_code: str, year: int, round: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.exam_code == exam_code).first()
    if not exam:
        raise HTTPException(status_code=404, detail="해당 시험코드 없음")

    exam_round = db.query(ExamRound).filter_by(exam_id=exam.id, year=year, round=round).first()
    if not exam_round:
        raise HTTPException(status_code=404, detail="해당 회차 없음")

    round_subjects = db.query(RoundSubject).filter_by(exam_round_id=exam_round.id).all()

    result = []
    for rs in round_subjects:
        questions = db.query(Question).filter_by(round_subject_id=rs.id).order_by(Question.question_no).all()
        subject_name = rs.subject.subject_name

        for q in questions:
            choices = (
                db.query(Choice)
                .filter_by(question_id=q.id)
                .order_by(Choice.choice_number)
                .all()
            )

            answer = db.query(Answer).filter_by(question_id=q.id).first()
            answer_number = answer.choice_number if answer and 1 <= answer.choice_number <= 5 else None

            result.append({
                "question_id": q.id,
                "question_no": q.question_no,
                "question_text": q.question_text,
                "subject_name": subject_name,
                "choices": [c.choice_content for c in choices],
                "answer": answer_number
            })

    return {"questions": result}

@router.post("/admin/update-questions")
def update_questions(payload: UpdateQuestionRequest, db: Session = Depends(get_db)):
    try:
        for item in payload.questions:
            q = db.query(Question).filter_by(id=item.question_id).first()
            if not q:
                continue

            q.question_text = item.question_text

            # 기존 보기 삭제 후 다시 추가
            db.query(Choice).filter_by(question_id=q.id).delete()
            for idx, c in enumerate(item.choices):
                db.add(Choice(
                    question_id=q.id,
                    choice_number=idx + 1,
                    choice_content=c
                ))

            # 정답도 갱신
            existing_answer = db.query(Answer).filter_by(question_id=q.id).first()
            if existing_answer:
                existing_answer.choice_number = item.answer
            else:
                db.add(Answer(
                    question_id=q.id,
                    choice_number=item.answer
                ))

        db.commit()
        return {"message": "수정 완료"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
