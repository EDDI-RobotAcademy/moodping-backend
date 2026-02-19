from authentication.service.authentication_service import AuthenticationService
from authentication.jwt.jwt_handler import create_access_token, decode_token


class AuthenticationServiceImpl(AuthenticationService):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "AuthenticationServiceImpl":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_session(self, user_id: int, kakao_id: str) -> str:
        return create_access_token(user_id, kakao_id)

    def validate_session(self, token: str) -> int | None:
        payload = decode_token(token)
        if not payload or "sub" not in payload:
            return None
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            return None

    def get_payload(self, token: str) -> dict | None:
        return decode_token(token)
