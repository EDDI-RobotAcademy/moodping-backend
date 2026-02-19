from fastapi import APIRouter, Depends, HTTPException, Response, Request

from account.service.account_service_impl import AccountServiceImpl
from authentication.service.authentication_service_impl import AuthenticationServiceImpl
from account.domain.value_objects.email import Email
from account.domain.value_objects.nickname import Nickname

account_router = APIRouter(prefix="/account")


# DI
def inject_auth_service() -> AuthenticationServiceImpl:
    return AuthenticationServiceImpl.get_instance()

def inject_account_service() -> AccountServiceImpl:
    return AccountServiceImpl.get_instance()


@account_router.post("/sign-up")
async def signup(
    request: Request,
    response: Response,
    auth_service: AuthenticationServiceImpl = Depends(inject_auth_service),
    account_service: AccountServiceImpl = Depends(inject_account_service),
):
    # 쿠키에서 temp_token 읽기
    temp_token = request.cookies.get("tempToken")
    if not temp_token:
        raise HTTPException(status_code=400, detail="tempToken cookie is required")

    # Body 검증
    body = await request.json()

    email_raw = body.get("email")
    nickname_raw = body.get("nickname")
    login_type = body.get("login_type")

    if not all([email_raw, nickname_raw, login_type]):
        raise HTTPException(
            status_code=400,
            detail="email, nickname, login_type required"
        )

    # 임시 세션 검증
    kakao_access_token = auth_service.get_temp_session(temp_token)
    if not kakao_access_token:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired temporary token"
        )

    # Aggregate 생성 (Service 내부에서 세션 처리)
    account = account_service.register(
        login_type=login_type,
        email=Email(email_raw),
        nickname=Nickname(nickname_raw),
    )

    # temp 세션 제거
    auth_service.delete_temp_session(temp_token)

    response.delete_cookie(
        key="tempToken",
        path="/",
        httponly=True,
        secure=True,
        samesite="lax"
    )

    # user 세션 발급
    user_token = auth_service.create_session(
        account.id,
        kakao_access_token
    )

    response.set_cookie(
        key="userToken",
        value=user_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    # Enum 직렬화 안전 처리
    login_type_value = (
        account.login_type.value
        if hasattr(account.login_type, "value")
        else account.login_type
    )

    return {
        "email": account.profile.email,
        "nickname": account.profile.nickname,
        "login_type": login_type_value,
        "is_temp_user": False,
    }
