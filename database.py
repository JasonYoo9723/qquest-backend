# qquest-backend\database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import sys
from dotenv import load_dotenv
from typing import Generator

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    try:
        print("⚙️ DB 연결 시도 중...", file=sys.stderr, flush=True)
        db = SessionLocal()
        yield db
    except Exception as e:
        print("❌ DB 연결 실패:", repr(e), file=sys.stderr, flush=True)
        raise
    finally:
        print("⚙️ DB 연결 종료", file=sys.stderr, flush=True)
        db.close()
        