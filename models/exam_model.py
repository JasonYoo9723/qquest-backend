# models\exam_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID
from models.category_model import Category

# 자격증
class Exam(Base):
    __tablename__ = 't_exam'

    id = Column(Integer, primary_key=True, index=True)
    exam_code = Column(String(50), unique=True, index=True, nullable=False)
    exam_name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('t_category.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship('Category', back_populates='exams')
    rounds = relationship('ExamRound', back_populates='exam')
    subjects = relationship("Subject", back_populates="exam")