# schemas/user_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class SignUpRequest(BaseModel):
    email: EmailStr
    name: str
    provider: str  # e.g. 'google'
    provider_id: str  # 구글의 sub (user_id)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    provider: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class GoogleLoginRequest(BaseModel):
    id_token: str
