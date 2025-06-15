# models\question_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

# 문제 테이블
class Question(Base):
    __tablename__ = "t_question"

    id = Column(Integer, primary_key=True, index=True)
    round_subject_id = Column(Integer, ForeignKey("t_round_subject.id", ondelete="CASCADE"), nullable=False)
    question_no = Column(Integer, nullable=False)
    question_text = Column(String, nullable=False)
    question_answer = Column(String)

    round_subject = relationship("RoundSubject", back_populates="questions")
    choices = relationship("Choice", back_populates="question", cascade="all, delete-orphan")
    answer = relationship("Answer", uselist=False, back_populates="question", cascade="all, delete")
    wrong_notes = relationship("WrongNote", back_populates="question", cascade="all, delete")