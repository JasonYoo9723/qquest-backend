# models\exam_round_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

# 자격증 회차
class ExamRound(Base):
    __tablename__ = 't_exam_round'

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey('t_exam.id'), nullable=False)
    year = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    exam = relationship('Exam', back_populates='rounds')
    round_subjects = relationship('RoundSubject', back_populates='exam_round')