from config.settings import settings


class KakaoConfig:
    AUTH_BASE_URL = "https://kauth.kakao.com/oauth/authorize"

    @classmethod
    def get_client_id(cls) -> str:
        return settings.KAKAO_CLIENT_ID

    @classmethod
    def get_redirect_uri(cls) -> str:
        return settings.KAKAO_REDIRECT_URI
