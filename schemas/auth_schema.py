# dependencies/schemas/auth_schema.py
from pydantic import BaseModel

class GoogleLoginRequest(BaseModel):
    credential: str
