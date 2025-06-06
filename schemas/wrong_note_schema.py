from pydantic import BaseModel
from typing import List
from datetime import datetime

class WrongNoteBase(BaseModel):
    question_id: int
    
class WrongNoteAddRequest(BaseModel):
    user_id: str
    question_id: int

class WrongNoteRemoveRequest(BaseModel):
    user_id: str
    question_id: int

class WrongNoteResponse(BaseModel):
    id: int
    question_id: int
    question_text: str
    choices: List[str]
    answer: int
    created_at: datetime
