from pydantic import BaseModel
from datetime import datetime

class ExamRoundBase(BaseModel):
    exam_id: int
    year: int
    round: int

class ExamRoundCreate(ExamRoundBase):
    pass

class ExamRoundUpdate(ExamRoundBase):
    pass

class ExamRoundOut(ExamRoundBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
