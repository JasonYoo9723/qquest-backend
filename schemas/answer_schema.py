# schemas/answer_schema.py
from pydantic import BaseModel
from typing import List

class SingleAnswer(BaseModel):
    question_number: int
    answers: List[int]

class AnswerUploadRequest(BaseModel):
    exam_code: str
    year: int
    round: int
    session: int
    answers: List[SingleAnswer]
