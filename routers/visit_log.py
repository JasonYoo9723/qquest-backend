# src/routes/visit_log.py
from fastapi import APIRouter, Request, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
from models.visit_log_model import VisitLog
from models.user_model import User
from database import get_db
from schemas.visit_log_schema import VisitLogCreate, VisitLogResponse
from typing import Optional
from dependencies.auth import get_optional_user
from sqlalchemy import text

router = APIRouter()

@router.post("/visit", status_code=status.HTTP_201_CREATED, response_model=VisitLogResponse)
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

@router.get("/visit/stats/daily")
def get_daily_stats(db: Session = Depends(get_db)):
    sql = """
    SELECT
        DATE(visited_at) AS date,
        COUNT(*) AS pageviews,
        COUNT(DISTINCT ip) AS unique_visitors
    FROM t_visit_logs
    GROUP BY DATE(visited_at)
    ORDER BY DATE(visited_at) DESC
    LIMIT 30
    """
    result = db.execute(text(sql)).fetchall()
    return [{"date": str(r[0]), "pv": r[1], "uv": r[2]} for r in result]

@router.get("/visit/stats/monthly")
def get_monthly_stats(db: Session = Depends(get_db)):
    sql = """
    SELECT
        TO_CHAR(visited_at, 'YYYY-MM') AS month,
        COUNT(*) AS pageviews,
        COUNT(DISTINCT ip) AS unique_visitors
    FROM t_visit_logs
    GROUP BY TO_CHAR(visited_at, 'YYYY-MM')
    ORDER BY month DESC
    LIMIT 12
    """
    result = db.execute(text(sql)).fetchall()
    return [{"month": r[0], "pv": r[1], "uv": r[2]} for r in result]


@router.get("/visit/stats/exam")
def get_exam_stats(db: Session = Depends(get_db)):
    sql = """
    SELECT
        v.exam_code,
        e.exam_name,
        COUNT(*) AS visit_count
    FROM t_visit_logs v
    JOIN t_exams e ON v.exam_code = e.exam_code
    GROUP BY v.exam_code, e.exam_name
    ORDER BY visit_count DESC
    """
    result = db.execute(sql).fetchall()
    return [{"exam_code": r[0], "exam_name": r[1], "count": r[2]} for r in result]
