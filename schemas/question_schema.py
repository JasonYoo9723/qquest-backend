from pydantic import BaseModel
from typing import List, Optional

# 보기 생성용 스키마
class ChoiceCreate(BaseModel):
    choice_content: str

# 문제 생성용 스키마
class QuestionCreate(BaseModel):
    subject_code: str                     # 필수: 회차-과목 매핑에 필요
    question_no: int                      # 필수: 번호
    question_text: str                   # 필수: 문제 지문
    choices: List[ChoiceCreate]          # 필수: 보기 목록
    question_answer: Optional[str] = None  # 선택사항

# 업로드 요청 전체 스키마
class UploadRequest(BaseModel):
    exam_code: str
    year: int
    round: int
    questions: List[QuestionCreate]

# 과목 목록 조회용 응답 스키마
class SubjectResponse(BaseModel):
    subject_name: str
    subject_code: str
