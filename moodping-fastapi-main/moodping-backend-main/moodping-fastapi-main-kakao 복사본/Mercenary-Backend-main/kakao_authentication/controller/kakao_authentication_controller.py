from fastapi import APIRouter, Depends, Query, HTTPException, Response
from starlette.responses import RedirectResponse

from account.domain.value_objects.login_type import LoginType
from account.domain.value_objects.email import Email
from account.domain.value_objects.nickname import Nickname
from account.service.account_service_impl import AccountServiceImpl
from authentication.service.authentication_service_impl import AuthenticationServiceImpl
from config.settings import get_settings
from kakao_authentication.service.kakao_authentication_service_impl import KakaoAuthenticationServiceImpl

kakao_authentication_router = APIRouter(prefix="/kakao-authentication")

def inject_kakao_authentication_service() -> KakaoAuthenticationServiceImpl:
    return KakaoAuthenticationServiceImpl.getInstance()

def inject_authentication_service() -> AuthenticationServiceImpl:
    return AuthenticationServiceImpl.get_instance()

def inject_account_service() -> AccountServiceImpl:
    return AccountServiceImpl.get_instance()

@kakao_authentication_router.get("/request-oauth-link")
def request_oauth_link(
    kakao_service: KakaoAuthenticationServiceImpl =
    Depends(inject_kakao_authentication_service)
):
    oauth_url = kakao_service.generate_oauth_url()

    # return {
    #     "kakao_oauth_url": oauth_url
    # }

    return RedirectResponse(oauth_url)

@kakao_authentication_router.get("/request-access-token-after-redirection")
def request_access_token_after_redirection(
    response: Response,
    code: str = Query(...),
    kakao_service: KakaoAuthenticationServiceImpl = Depends(inject_kakao_authentication_service),
    auth_service: AuthenticationServiceImpl = Depends(inject_authentication_service),
    account_service: AccountServiceImpl = Depends(inject_account_service)
):
    try:
        # Kakao API로 로그인 & 사용자 정보 조회
        kakao_user_info = kakao_service.login_with_kakao(code)
        email = Email(kakao_user_info.email)

        print(type(kakao_user_info))
        print(kakao_user_info)

        # Account 조회: 기존 회원인지 확인
        account = account_service.find_by_email_and_login_type(
            email=email,
            login_type=LoginType.KAKAO.value
        )

        print("Account:", account)

        settings = get_settings()

        if account is None:
            temp_token = auth_service.create_temp_session(
                kakao_user_info.access_token
            )

            response = RedirectResponse(
                url=f"{settings.FRONTEND_URL}/account/signup"
            )

            response.set_cookie(
                key="tempToken",
                value=temp_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=int(
                    AuthenticationServiceImpl.TEMP_SESSION_TTL.total_seconds()
                )
            )

            return response

        account_id = account.id

        # 인증 세션 (Redis)
        user_token = auth_service.create_session(
            account_id,
            kakao_user_info.access_token
        )

        response = RedirectResponse(settings.FRONTEND_URL)
        response.set_cookie(
            key="userToken",
            value=user_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")