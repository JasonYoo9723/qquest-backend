# qquest-backend\main.py
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from models.exam_model import Exam, Subject, Question, Choice
from schemas import UploadRequest
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
import sys
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 라우터 설정
router = APIRouter(prefix="/api")

# ✅ 예외 핸들러 - 모든 예외
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🔥 에러 발생:", repr(exc), file=sys.stderr, flush=True)
    return JSONResponse(status_code=500, content={"detail": str(exc)})

# ✅ 예외 핸들러 - 요청 유효성 오류 (ValidationError)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("💥 요청 유효성 검사 실패:", exc, file=sys.stderr, flush=True)
    # 응답 형태를 명시적으로 보여주자
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

# ✅ 요청 진입 로그를 위한 미들웨어
@app.middleware("http")
async def log_request(request: Request, call_next):
    print(f"➡️ {request.method} {request.url.path}", file=sys.stderr, flush=True)
    response = await call_next(request)
    return response

@router.get("/learn/random-question")
def get_random_question(db: Session = Depends(get_db)):
    from sqlalchemy.sql.expression import func
    question = db.query(Question).order_by(func.random()).first()

    if not question:
        raise HTTPException(status_code=404, detail="문제가 없습니다.")

    exam = question.subject.exam  # <-- 관계를 따라가면서 exam 정보 가져오기

    return {
        "id": question.id,
        "question_no": question.question_no,
        "question_text": question.question_text,
        "subject_name": question.subject.subject_name,
        "exam_name": exam.exam_name,
        "year": exam.year,
        "round": exam.round,
        "choices": [
            {
                "number": c.choice_number,
                "content": c.choice_content
            } for c in sorted(question.choices, key=lambda x: x.choice_number)
        ],
        "answer": question.question_answer  # 정답 번호 (예: "2")
    }

# ✅ 문제 저장 API
@router.post("/admin/save-questions")
def save_questions(payload: UploadRequest, db: Session = Depends(get_db)):
    print("🔥 save_questions 진입", file=sys.stderr, flush=True)

    try:
        exam = Exam(
            exam_name=payload.exam_name,
            year=payload.year,
            round=payload.round,
            exam_code=f"{payload.exam_name}-{payload.year}-{payload.round}"
        )
        db.add(exam)
        db.flush()  # exam.id 확보

        subject_map = {}

        for q in payload.questions:
            subject_name = q.subject_name.strip()
            print(f"✅ 처리 중인 문제 번호: {q.question_no}", file=sys.stderr, flush=True)

            # 과목 처리
            if subject_name not in subject_map:
                subject = Subject(subject_name=subject_name, exam_id=exam.id)
                db.add(subject)
                db.flush()
                subject_map[subject_name] = subject
            else:
                subject = subject_map[subject_name]

            # 문제 저장
            question = Question(
                question_no=q.question_no,
                question_text=q.question_text,
                subject_id=subject.id
            )
            db.add(question)
            db.flush()

            # 보기 저장
            for idx, choice in enumerate(q.choices):
                db.add(Choice(
                    question_id=question.id,
                    choice_number=idx + 1,
                    choice_content=choice.choice_content
                ))

        db.commit()
        return {"message": "저장 완료"}

    except Exception as e:
        db.rollback()
        print("🔥 내부 저장 에러:", repr(e), file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ✅ 라우터 등록
app.include_router(router)
