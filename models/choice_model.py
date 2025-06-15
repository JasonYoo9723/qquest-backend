# models\choice_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

# 보기
class Choice(Base):
    __tablename__ = "t_choice"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("t_question.id", ondelete="CASCADE"), nullable=False)
    choice_number = Column(Integer)
    choice_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="choices")