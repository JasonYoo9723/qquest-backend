from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.question_model import Question
from models.choice_model import Choice
from models.answer_model import Answer
from models.wrong_note_model import WrongNote
from models.user_model import User
from schemas.wrong_note_schema import WrongNoteBase, WrongNoteResponse
from dependencies.auth import get_current_user
import random

router = APIRouter()

# ✅ 오답노트에 추가
@router.post("/wrong-note/add")
def add_wrong_note(
    note: WrongNoteBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exists = db.query(WrongNote).filter_by(
        user_id=current_user.id, question_id=note.question_id
    ).first()
    if not exists:
        db.add(WrongNote(user_id=current_user.id, question_id=note.question_id))
        db.commit()
    return {"status": "added"}

# ✅ 오답노트에서 삭제
@router.post("/wrong-note/remove")
def remove_wrong_note(
    note: WrongNoteBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(WrongNote).filter_by(
        user_id=current_user.id, question_id=note.question_id
    ).delete()
    db.commit()
    return {"status": "removed"}

# ✅ 오답노트 목록 조회
@router.get("/wrong-note/list", response_model=WrongNoteResponse)
def get_wrong_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notes = (
        db.query(Question)
        .join(WrongNote, WrongNote.question_id == Question.id)
        .filter(WrongNote.user_id == current_user.id)
        .all()
    )

    result = []
    for q in notes:
        round_subject = q.round_subject
        subject = round_subject.subject
        exam_round = round_subject.exam_round
        exam = exam_round.exam
        choices = db.query(Choice).filter_by(question_id=q.id).order_by(Choice.choice_number).all()
        answer = db.query(Answer).filter_by(question_id=q.id).first()

        result.append({
            "question_id": q.id,
            "question_no": q.question_no,
            "question_text": q.question_text,
            "choices": [
                {"number": c.choice_number, "content": c.choice_content}
                for c in choices
            ],
            "answer": answer.choice_number if answer else None,
            "exam_name": exam.exam_name,
            "year": exam_round.year,
            "round": exam_round.round,
            "subject_name": subject.subject_name
        })

    return {"questions": result}

@router.get("/wrong-note/next-question", response_model=dict)
def get_next_wrong_note_question(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wrong_notes = (
        db.query(WrongNote)
        .filter(WrongNote.user_id == current_user.id)
        .all()
    )

    if not wrong_notes:
        raise HTTPException(status_code=404, detail="오답노트가 비어 있습니다.")

    random_note = random.choice(wrong_notes)
    question = db.query(Question).filter_by(id=random_note.question_id).first()

    round_subject = question.round_subject
    subject = round_subject.subject
    exam_round = round_subject.exam_round
    exam = exam_round.exam

    choices = db.query(Choice).filter_by(question_id=question.id).order_by(Choice.choice_number).all()
    answer = db.query(Answer).filter_by(question_id=question.id).first()

    return {
        "question_id": question.id,
        "question_no": question.question_no,
        "question_text": question.question_text,
        "choices": [
            {"number": c.choice_number, "content": c.choice_content}
            for c in choices
        ],
        "answer": answer.choice_number if answer else None,
        "exam_name": exam.exam_name,
        "year": exam_round.year,
        "round": exam_round.round,
        "subject_name": subject.subject_name,
    }
