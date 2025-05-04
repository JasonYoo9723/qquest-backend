### 📄 파일: schemas/question_schema.py

from pydantic import BaseModel
from typing import List

class ChoiceCreate(BaseModel):
    choice_content: str

class QuestionCreate(BaseModel):
    subject_code: str
    question_no: int
    question_text: str
    choices: List[ChoiceCreate]
    question_answer: str

class UploadRequest(BaseModel):
    exam_code: str
    year: int
    round: int
    questions: List[QuestionCreate]
