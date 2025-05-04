# models/user_model.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "t_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # google, kakao, naver
    provider_id = Column(String(100), nullable=False)  # 구글 id 토큰 등의 고유값
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
