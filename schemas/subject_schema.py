from pydantic import BaseModel
from datetime import datetime

class SubjectBase(BaseModel):
    subject_code: str
    subject_name: str
    exam_id: int

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(SubjectBase):
    pass

class SubjectOut(SubjectBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
