# models\round_subject_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

# 회차-과목-교시 연결
class RoundSubject(Base):
    __tablename__ = 't_round_subject'

    id = Column(Integer, primary_key=True)
    exam_round_id = Column(Integer, ForeignKey('t_exam_round.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('t_subject.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    exam_round = relationship('ExamRound', back_populates='round_subjects')
    subject = relationship('Subject', back_populates='round_subjects')
    questions = relationship('Question', back_populates='round_subject')