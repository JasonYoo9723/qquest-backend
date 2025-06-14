# main.py
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import sys
from routers.public import wrong_notes
from database import engine, Base
from dotenv import load_dotenv

from routers.admin import answer, modify, visit_log, category, exam, subject, exam_round, round_subject
from routers.auth import auth
from routers.public import exam_meta, question
from routers.user import user

load_dotenv()

# DB 모델 테이블 생성 (자동)
Base.metadata.create_all(bind=engine)


app = FastAPI()

# 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🔥 에러 발생:", repr(exc), file=sys.stderr, flush=True)
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("💥 요청 유효성 검사 실패:", exc, file=sys.stderr, flush=True)
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "body": exc.body})

# 라우터 등록
app.include_router(question.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(answer.router, prefix="/api")
app.include_router(modify.router, prefix="/api", tags=["AdminModify"])
app.include_router(wrong_notes.router, prefix="/api")
app.include_router(exam_meta.router, prefix="/api")
app.include_router(visit_log.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(exam.router, prefix="/api")
app.include_router(subject.router, prefix="/api")
app.include_router(exam_round.router, prefix="/api")
app.include_router(round_subject.router, prefix="/api")

origins = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # ✅ 환경변수 기반 설정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)