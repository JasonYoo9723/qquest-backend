# schemas/visit_log_schema.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VisitLogCreate(BaseModel):
    user_agent: Optional[str] = None
    exam_code: Optional[str] = None
    path: Optional[str] = None

class VisitLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    ip: str
    user_agent: Optional[str] = None
    exam_code: Optional[str] = None
    path: Optional[str] = None
    visited_at: datetime

    class Config:
        orm_mode = True