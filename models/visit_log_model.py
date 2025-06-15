# models/visit_log_model.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# 방문 로그
class VisitLog(Base):
    __tablename__ = "t_visit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("t_user.id"), nullable=True)
    ip = Column(String(100), nullable=False)
    user_agent = Column(String(300), nullable=True)
    exam_code = Column(String(50), nullable=True)
    path = Column(String, nullable=True)
    visited_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="visit_logs")