# models\exam_wrong_question_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

# 시험 결과 - 틀린 문제 - 선택한 답
class ExamWrongQuestion(Base):
    __tablename__ = "t_exam_wrong_question"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("t_exam_result.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("t_question.id"), nullable=False)
    chosen_choice = Column(Integer, nullable=False)

    exam_result = relationship("ExamResult", backref="wrong_questions")
    question = relationship("Question")