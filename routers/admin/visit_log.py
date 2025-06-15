# routers\admin\visit_log.py
from fastapi import APIRouter, Request, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database import get_db

from models.visit_log_model import VisitLog
from models.user_model import User
from models.exam_model import Exam
from schemas.visit_log_schema import VisitLogCreate, VisitLogResponse
from dependencies.auth import get_optional_user
from sqlalchemy import func

router = APIRouter(
    prefix="/admin/visit",
    tags=["Admin VisitLog"],
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=VisitLogResponse)
def log_visit(
    log_data: VisitLogCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    ip = request.client.host

    visit = VisitLog(
        user_id=current_user.id if current_user else None,
        ip=ip,
        user_agent=log_data.user_agent or request.headers.get("user-agent", None),
        exam_code=log_data.exam_code,
        path=log_data.path or request.url.path,
        visited_at=datetime.utcnow()
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


@router.get("/stats/daily")
def get_daily_stats(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.date(VisitLog.visited_at).label("date"),
            func.count().label("pv"),
            func.count(func.distinct(VisitLog.ip)).label("uv")
        )
        .group_by(func.date(VisitLog.visited_at))
        .order_by(func.date(VisitLog.visited_at).desc())
        .limit(30)
        .all()
    )
    return [{"date": str(r.date), "pv": r.pv, "uv": r.uv} for r in rows]


@router.get("/stats/monthly")
def get_monthly_stats(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.to_char(VisitLog.visited_at, 'YYYY-MM').label("month"),
            func.count().label("pv"),
            func.count(func.distinct(VisitLog.ip)).label("uv")
        )
        .group_by(func.to_char(VisitLog.visited_at, 'YYYY-MM'))
        .order_by(func.to_char(VisitLog.visited_at, 'YYYY-MM').desc())
        .limit(12)
        .all()
    )
    return [{"month": r.month, "pv": r.pv, "uv": r.uv} for r in rows]


@router.get("/stats/exam")
def get_exam_stats(db: Session = Depends(get_db)):
    rows = (
        db.query(
            VisitLog.exam_code,
            Exam.exam_name,
            func.count().label("count")
        )
        .join(Exam, VisitLog.exam_code == Exam.exam_code)
        .group_by(VisitLog.exam_code, Exam.exam_name)
        .order_by(func.count().desc())
        .all()
    )
    return [{"exam_code": r.exam_code, "exam_name": r.exam_name, "count": r.count} for r in rows]
