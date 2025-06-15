from pydantic import BaseModel
from datetime import datetime

class RoundSubjectBase(BaseModel):
    exam_round_id: int
    subject_id: int

class RoundSubjectCreate(RoundSubjectBase):
    pass

class RoundSubjectUpdate(RoundSubjectBase):
    pass

class RoundSubjectOut(RoundSubjectBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
