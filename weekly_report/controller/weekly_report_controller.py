from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from moodping.authentication.controller.authentication_controller import get_current_user_payload_optional
from moodping.weekly_report.service.weekly_report_service_impl import WeeklyReportServiceImpl
from moodping.config.mysql_config import get_db

weekly_report_router = APIRouter(prefix="/api/reports", tags=["reports"])


def inject_weekly_report_service() -> WeeklyReportServiceImpl:
    return WeeklyReportServiceImpl.get_instance()


@weekly_report_router.get("/weekly/latest")
async def get_latest_weekly_report(
    payload: dict | None = Depends(get_current_user_payload_optional),
    weekly_report_service: WeeklyReportServiceImpl = Depends(inject_weekly_report_service),
):
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    account_id = int(payload.get("sub"))

    try:
        report = await weekly_report_service.get_or_create_latest_report(user_id=account_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
