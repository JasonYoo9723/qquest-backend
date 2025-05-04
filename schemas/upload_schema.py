# schemas/upload_schema.py
from pydantic import BaseModel
from typing import List

class ChoiceItem(BaseModel):
    choice_content: str

class QuestionItem(BaseModel):
    subject_code: str
    question_no: int
    question_text: str
    question_answer: str
    choices: List[ChoiceItem]

class UploadRequest(BaseModel):
    exam_code: str
    year: int
    round: int
    questions: List[QuestionItem]
