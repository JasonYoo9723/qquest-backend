from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.exam_model import Exam, ExamRound, RoundSubject, Question, Answer
from schemas.answer_schema import AnswerUploadRequest

router = APIRouter()

@router.post("/admin/upload-answers")
def upload_answers(payload: AnswerUploadRequest, db: Session = Depends(get_db)):
    # 1. 시험코드로 exam_id 조회
    exam = db.query(Exam).filter_by(exam_code=payload.exam_code).first()
    if not exam:
        raise HTTPException(status_code=404, detail="해당 시험코드를 찾을 수 없습니다.")

    # 2. 연도 + 회차로 exam_round 조회
    exam_round = db.query(ExamRound).filter_by(
        exam_id=exam.id,
        year=payload.year,
        round=payload.round
    ).first()
    if not exam_round:
        raise HTTPException(status_code=404, detail="해당 시험의 회차 정보를 찾을 수 없습니다.")

    # 3. exam_round_id + session 에 해당하는 round_subject 목록 조회
    round_subjects = db.query(RoundSubject).filter_by(
        exam_round_id=exam_round.id,
        session=payload.session  # ← 교시 추가 조건
    ).all()
    if not round_subjects:
        raise HTTPException(status_code=404, detail="해당 교시에 대한 과목이 없습니다.")

    round_subject_ids = [rs.id for rs in round_subjects]

    # 4. 문제번호 기준으로 정답 저장
    for item in payload.answers:
        question = db.query(Question).filter(
            Question.round_subject_id.in_(round_subject_ids),
            Question.question_no == item.question_number
        ).first()

        if not question:
            raise HTTPException(status_code=404, detail=f"{item.question_number}번 문제를 찾을 수 없습니다.")

        # 기존 정답 삭제
        db.query(Answer).filter_by(question_id=question.id).delete()

        # 새 정답 등록
        for choice_number in item.answers:
            db.add(Answer(question_id=question.id, choice_number=choice_number))

    db.commit()
    return {"message": "정답이 성공적으로 저장되었습니다."}

