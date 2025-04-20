from pydantic import BaseModel
from typing import List

class ChoiceCreate(BaseModel):
    choice_content: str

class QuestionCreate(BaseModel):
    question_no: int
    question_text: str
    subject_name: str
    choices: List[ChoiceCreate]

class UploadRequest(BaseModel):
    exam_code: str
    year: int
    round: int
    questions: List[QuestionCreate]
