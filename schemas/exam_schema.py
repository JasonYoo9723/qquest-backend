from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExamBase(BaseModel):
    exam_code: str
    exam_name: str
    category_id: int

class ExamCreate(ExamBase):
    pass

class ExamUpdate(ExamBase):
    pass

class ExamResponse(ExamBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
