# <!-- qquest-backend/dependencies/auth.py -->
from fastapi import Header, HTTPException, Depends
from utils.jwt import decode_access_token
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import User

def get_current_user(
    Authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    
    token = Authorization.split(" ")[1]
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
