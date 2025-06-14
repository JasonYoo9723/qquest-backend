# schemas\question_schema.py
from pydantic import BaseModel
from typing import List
from typing import Optional
from datetime import datetime

class ChoiceItem(BaseModel):
    choice_content: str


class QuestionItem(BaseModel):
    subject_code: str
    question_no: int
    question_text: str
    question_answer: int | None = None
    choices: List[ChoiceItem]


class UploadRequest(BaseModel):
    exam_code: str
    year: int
    round: int
    session: int
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


class StartExamRequest(BaseModel):
    exam_code: str
    year: int = 0
    round: int = 0
    session: int = 0
    subject: str = ""
    count: int = 10

class ExamFilterRequest(BaseModel):
    exam_code: str
    year: Optional[int] = 0
    round: Optional[int] = 0
    session: Optional[int] = 0
    subject: Optional[str] = ""
    count: Optional[int] = 10  # only used for /exam/start

class ExamResultCreate(BaseModel):
    exam_code: str
    year: Optional[int]
    round: Optional[int]
    session: Optional[int]
    subject: Optional[str]
    total_count: int
    correct_count: int
    wrong_count: int
    duration_seconds: int

class ExamWrongQuestionDetailed(BaseModel):
    question_id: int
    question_text: str
    question_no: int
    choices: List[str]
    chosen_choice: int
    correct_choice: int
    
class ExamResultOut(BaseModel):
    id: int
    exam_code: str
    exam_name: Optional[str]  # 추가
    year: Optional[int]
    round: Optional[int]
    session: Optional[int]
    subject: Optional[str]
    subject_name: Optional[str]  # 추가
    total_count: int
    correct_count: int
    wrong_count: int
    duration_seconds: int
    taken_at: datetime
    wrong_questions: List[ExamWrongQuestionDetailed]

class WrongQuestionCreate(BaseModel):
    question_id: int
    chosen_choice: int

class ExamResultCreate(BaseModel):
    exam_code: str
    year: Optional[int]
    round: Optional[int]
    session: Optional[int]
    subject: Optional[str]
    total_count: int
    correct_count: int
    wrong_count: int
    duration_seconds: int
    wrong_questions: List[WrongQuestionCreate]

class ExamWrongQuestionOut(WrongQuestionCreate):
    id: int
