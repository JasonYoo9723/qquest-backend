# dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.orm import Session
from models.user_model import User
from db.session import get_db
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # 사용 안 해도 됨

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

if not GOOGLE_CLIENT_ID:
    raise RuntimeError("환경변수 GOOGLE_CLIENT_ID 가 설정되지 않았습니다.")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        # 1. Google ID 토큰 검증
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        email = idinfo.get("email")
        name = idinfo.get("name")
        provider_id = idinfo.get("sub")  # ✅ Google 고유 사용자 ID
        provider = "google"

        if not email or not provider_id:
            raise ValueError("이메일 또는 provider_id 누락")

        # 2. DB에서 사용자 검색
        user = db.query(User).filter_by(email=email).first()

        # 3. 없으면 새로 등록
        if not user:
            user = User(
                email=email,
                name=name,
                provider=provider,
                provider_id=provider_id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user

    except Exception as e:
        print(f"❌ Google 토큰 검증 또는 사용자 처리 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
