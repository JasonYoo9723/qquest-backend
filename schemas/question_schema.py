# schemas\question_schema.py
from pydantic import BaseModel
from typing import List


class ChoiceItem(BaseModel):
    choice_content: str


class QuestionItem(BaseModel):
    subject_code: str
    question_no: int
    question_text: str
    question_answer: int
    choices: List[ChoiceItem]


class UploadRequest(BaseModel):
    exam_code: str
    year: int
    round: int
    questions: List[QuestionItem]


class SubjectResponse(BaseModel):
    subject_code: str
    subject_name: str
    
class QuestionUpdateItem(BaseModel):
    question_id: int
    question_text: str
    question_answer: int
    choices: List[str]

class UpdateQuestionRequest(BaseModel):
    questions: List[QuestionUpdateItem]