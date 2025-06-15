# models\answer_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

# 정답
class Answer(Base):
    __tablename__ = "t_answer"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("t_question.id", ondelete="CASCADE"), nullable=False)
    choice_number = Column(Integer, nullable=False)

    question = relationship("Question", back_populates="answer")