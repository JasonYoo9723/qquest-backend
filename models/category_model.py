# models\category_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID

# 카테고리
class Category(Base):
    __tablename__ = 't_category'

    id = Column(Integer, primary_key=True, index=True)
    category_code = Column(String(50), unique=True, index=True, nullable=False)
    category_name = Column(String(100), nullable=False)
    use_yn = Column(String(1), nullable=False, default='Y')
    created_at = Column(DateTime, default=datetime.utcnow)

    exams = relationship('Exam', back_populates='category')