# db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# .env 파일 로딩
load_dotenv()

# PostgreSQL 접속 URL (.env에서 가져옴)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("환경변수 DATABASE_URL이 설정되지 않았습니다.")

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI에서 사용하기 위한 DB 세션 의존성
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
