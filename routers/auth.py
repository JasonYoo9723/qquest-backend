# <!-- qquest-backend/routers/auth.py -->
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from models.user_model import User
from database import get_db
from utils.jwt import create_access_token
from dependencies.auth import get_current_user
from schemas.auth_schema import GoogleLoginRequest
import os

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

@router.get("/users/me")
def get_profile(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "is_admin": current_user.is_admin,
    }

@router.post("/auth/google-login")
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        token = payload.credential
        if not token:
            raise HTTPException(status_code=400, detail="Missing Google ID token")

        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)

        token_info = {
            "email": idinfo["email"],
            "name": idinfo.get("name", ""),
            "sub": idinfo["sub"]
        }

        user = db.query(User).filter(User.email == token_info["email"]).first()
        if not user:
            user = User(
                email=token_info["email"],
                name=token_info["name"],
                provider="google",
                provider_id=token_info["sub"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        jwt_token = create_access_token({
            "user_id": user.id,
            "email": user.email
        })

        return {
            "access_token": jwt_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
