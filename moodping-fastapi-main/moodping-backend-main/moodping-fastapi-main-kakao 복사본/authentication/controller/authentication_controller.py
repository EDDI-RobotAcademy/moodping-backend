"""
Authentication controller.
GET /auth/me: 현재 로그인 사용자 정보 (JWT 검증).
의존성: MP-01 완료 시 account_service 주입하여 nickname, profile_image 등 확장 가능.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from authentication.service.authentication_service_impl import AuthenticationServiceImpl

authentication_router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer(auto_error=False)


def inject_auth_service() -> AuthenticationServiceImpl:
    return AuthenticationServiceImpl.get_instance()


@authentication_router.get("/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth_service: AuthenticationServiceImpl = Depends(inject_auth_service),
):
    """현재 로그인 사용자 정보. Authorization: Bearer <access_token> 필요."""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authorization header required (Bearer token)")

    user_id = auth_service.validate_session(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    payload = auth_service.get_payload(credentials.credentials)
    kakao_id = (payload or {}).get("kakao_id") or ""

    # MP-01 account 도메인 연동 시 account_service.find_by_id로 nickname, profile_image 등 확장 가능
    return {
        "user_id": user_id,
        "kakao_id": kakao_id,
    }
