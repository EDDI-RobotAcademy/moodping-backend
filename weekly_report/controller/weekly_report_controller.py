from fastapi import APIRouter, Cookie, Depends, HTTPException

# Cross-domain: authentication/service (MP-04 완료 후 활성화)
from authentication.service.authentication_service_impl import AuthenticationServiceImpl
from weekly_report.service.weekly_report_service_impl import WeeklyReportServiceImpl

weekly_report_router = APIRouter(prefix="/weekly-report")


def inject_weekly_report_service() -> WeeklyReportServiceImpl:
    return WeeklyReportServiceImpl.get_instance()


def inject_auth_service() -> AuthenticationServiceImpl:
    return AuthenticationServiceImpl.get_instance()


def get_authenticated_account_id(
    userToken: str = Cookie(None),
    auth_service: AuthenticationServiceImpl = Depends(inject_auth_service),
) -> int:
    if not userToken:
        raise HTTPException(status_code=401, detail="Authentication required")

    account_id = auth_service.validate_session(userToken)

    if not account_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return account_id


@weekly_report_router.get("/latest")
async def get_latest_weekly_report(
    account_id: int = Depends(get_authenticated_account_id),
    weekly_report_service: WeeklyReportServiceImpl = Depends(inject_weekly_report_service),
):
    """
    이번 주 주간 리포트를 반환한다.
    - 이미 생성된 리포트가 있으면 그대로 반환
    - 없으면 mood_record 7일치로 LLM 요약을 생성한 뒤 저장하고 반환
    """
    try:
        report = await weekly_report_service.get_or_create_latest_report(user_id=account_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
