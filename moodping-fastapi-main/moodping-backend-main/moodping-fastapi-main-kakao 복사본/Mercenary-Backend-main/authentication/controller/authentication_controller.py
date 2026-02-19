from fastapi import APIRouter, Depends, Cookie, HTTPException

from authentication.service.authentication_service_impl import AuthenticationServiceImpl
from account.service.account_service_impl import AccountServiceImpl
from kakao_authentication.service.kakao_authentication_service_impl import (
    KakaoAuthenticationServiceImpl,
)

authentication_router = APIRouter(prefix="/authentication")


def inject_auth_service() -> AuthenticationServiceImpl:
    return AuthenticationServiceImpl.get_instance()


def inject_account_service() -> AccountServiceImpl:
    return AccountServiceImpl.get_instance()


def inject_kakao_service() -> KakaoAuthenticationServiceImpl:
    return KakaoAuthenticationServiceImpl.getInstance()


@authentication_router.get("/status")
def get_authentication_status(
    userToken: str | None = Cookie(default=None),
    tempToken: str | None = Cookie(default=None),
    auth_service: AuthenticationServiceImpl = Depends(inject_auth_service),
    account_service: AccountServiceImpl = Depends(inject_account_service),
    kakao_service: KakaoAuthenticationServiceImpl = Depends(inject_kakao_service),
):
    # 정회원 세션 확인
    if userToken:
        account_id = auth_service.validate_session(userToken)
        if not account_id:
            return {
                "logged_in": False,
                "is_temp_user": False,
                "email": None,
                "nickname": None,
                "login_type": None,
            }

        account = account_service.lookup(account_id)
        if not account:
            return {
                "logged_in": False,
                "is_temp_user": False,
                "email": None,
                "nickname": None,
                "login_type": None,
            }

        return {
            "logged_in": True,
            "is_temp_user": False,
            "email": account.profile.email.value,
            "nickname": account.profile.nickname.value,
            "login_type": account.login_type.value,
        }

    # 임시 세션 확인
    if tempToken:
        kakao_access_token = auth_service.get_temp_session(tempToken)
        if not kakao_access_token:
            return {
                "logged_in": False,
                "is_temp_user": False,
                "email": None,
                "nickname": None,
                "login_type": None,
            }

        account = kakao_service.get_user_info(kakao_access_token)

        return {
            "logged_in": False,
            "is_temp_user": True,
            "email": account.profile.email.value,
            "nickname": account.profile.nickname.value,
            "login_type": account.login_type.value,
        }

    # 쿠키 없음 → 로그인 안됨
    return {
        "logged_in": False,
        "is_temp_user": False,
        "email": None,
        "nickname": None,
        "login_type": None,
    }