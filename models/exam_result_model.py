# models\exam_result_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

# 시험결과
class ExamResult(Base):
    __tablename__ = "t_exam_result"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)

    exam_code = Column(String, ForeignKey("t_exam.exam_code"), nullable=False)
    year = Column(Integer, nullable=True)
    round = Column(Integer, nullable=True)
    session = Column(Integer, nullable=True)

    subject = Column(String, ForeignKey("t_subject.subject_code"), nullable=True)

    total_count = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    wrong_count = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    taken_at = Column(DateTime, default=datetime.utcnow)

    exam = relationship("Exam", lazy="joined")
    subject_obj = relationship("Subject", lazy="joined")