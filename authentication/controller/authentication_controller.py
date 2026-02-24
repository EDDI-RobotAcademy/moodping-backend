from fastapi import APIRouter, Depends, HTTPException, Header
import logging

from moodping.authentication.service.authentication_service import AuthenticationService
from moodping.authentication.service.authentication_service_impl import AuthenticationServiceImpl
from moodping.account.service.account_service_impl import AccountServiceImpl

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


def get_authentication_service() -> AuthenticationService:
    return AuthenticationServiceImpl()


def get_account_service() -> AccountServiceImpl:
    return AccountServiceImpl.get_instance()


def get_token_from_header(authorization: str | None = Header(None)) -> str | None:
    if not authorization:
        return None
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization


def get_current_user_payload(
    token: str | None = Depends(get_token_from_header),
    auth_service: AuthenticationService = Depends(get_authentication_service),
) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return auth_service.validate_session(token)


def get_current_user_payload_optional(
    token: str | None = Depends(get_token_from_header),
    auth_service: AuthenticationService = Depends(get_authentication_service),
) -> dict | None:
    """비로그인도 허용하는 Optional 인증"""
    if not token:
        return None
    try:
        return auth_service.validate_session(token)
    except HTTPException:
        return None


@router.get("/me")
def get_me(
    payload: dict = Depends(get_current_user_payload),
    account_service: AccountServiceImpl = Depends(get_account_service),
):
    user_id = int(payload.get("sub"))
    account = account_service.find_by_id(user_id)
    if not account:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    return {
        "id": account.id,
        "kakao_id": account.kakao_id,
        "nickname": account.nickname,
        "profile_image": account.profile_image,
    }
