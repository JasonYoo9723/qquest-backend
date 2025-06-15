# models\wrong_note_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

# 오답노트
class WrongNote(Base):
    __tablename__ = "t_wrong_note"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)  # Google user ID
    question_id = Column(Integer, ForeignKey("t_question.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question")