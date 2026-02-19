from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_optional
from app.domain.user.models import User
from app.domain.report.schemas import WeeklyReportResponse
from app.domain.report import service as report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/weekly/latest", response_model=WeeklyReportResponse)
async def get_latest_weekly_report(
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    user_id = user.id if user else None
    return await report_service.get_or_create_latest_report(user_id, db)
