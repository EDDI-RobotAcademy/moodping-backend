from urllib.parse import urlencode

from account.domain.entity.account import Account
from account.domain.entity.account_profile import AccountProfile
from account.domain.value_objects.email import Email
from account.domain.value_objects.login_type import LoginType
from account.domain.value_objects.nickname import Nickname
from config.settings import get_settings
from kakao_authentication.repository.kakao_authentication_repository_impl import KakaoAuthenticationRepositoryImpl
from kakao_authentication.service.kakao_authentication_service import (
    KakaoAuthenticationService,
)
from kakao_authentication.service.response.kakao_login_response import KakaoLoginResponse
from kakao_authentication.service.response.kakao_token_response import KakaoTokenResponse


class KakaoAuthenticationServiceImpl(KakaoAuthenticationService):

    __instance = None
    AUTH_BASE_URL = "https://kauth.kakao.com/oauth/authorize"

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.kakao_authentication_repository = (
                KakaoAuthenticationRepositoryImpl.getInstance()
            )

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def generate_oauth_url(self) -> str:
        settings = get_settings()

        params = {
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "response_type": "code",
        }

        return f"{self.AUTH_BASE_URL}?{urlencode(params)}"

    def request_access_token(self, code: str) -> KakaoTokenResponse:
        if not code:
            raise ValueError("인가 코드가 필요합니다.")

        token_data = self.kakao_authentication_repository.request_access_token(code)

        return KakaoTokenResponse(**token_data)

    def get_user_info(self, access_token: str) -> Account:
        user_info = self.kakao_authentication_repository.request_user_info(access_token)

        kakao_account = user_info.get("kakao_account", {})
        profile_info = kakao_account.get("profile", {})

        nickname = profile_info.get("nickname")
        email = kakao_account.get("email")

        if not nickname or not email:
            raise ValueError("Kakao 사용자 정보가 올바르지 않습니다.")

        return Account(
            id=None,
            profile=AccountProfile(
                nickname=Nickname(nickname),
                email=Email(email),
            ),
            login_type=LoginType.KAKAO,
        )

    def login_with_kakao(self, code: str) -> KakaoLoginResponse:
        if not code:
            raise ValueError("인가 코드가 필요합니다.")

        token_data = self.kakao_authentication_repository.request_access_token(code)

        access_token = token_data["access_token"]

        user_data = self.kakao_authentication_repository.request_user_info(access_token)

        kakao_account = user_data.get("kakao_account", {})
        profile = kakao_account.get("profile", {})

        return KakaoLoginResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_in=token_data["expires_in"],
            user_id=user_data["id"],
            nickname=profile.get("nickname"),
            email=kakao_account.get("email"),
        )