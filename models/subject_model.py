# models\subject_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID


# 과목
class Subject(Base):
    __tablename__ = 't_subject'

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String(50), unique=True, nullable=False)
    subject_name = Column(String(100), nullable=False)
    exam_id = Column(Integer, ForeignKey("t_exam.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    exam = relationship("Exam", back_populates="subjects")
    round_subjects = relationship("RoundSubject", back_populates="subject")
    exam_results = relationship("ExamResult", back_populates="subject_obj")