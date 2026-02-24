from typing import Dict, Any
from fastapi import HTTPException

from moodping.authentication.service.authentication_service import AuthenticationService
from moodping.authentication.jwt.jwt_handler import create_access_token, decode_token

class AuthenticationServiceImpl(AuthenticationService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AuthenticationServiceImpl, cls).__new__(cls)
        return cls._instance

    def create_session(self, user_id: int, kakao_id: str) -> str:
        return create_access_token(user_id, kakao_id)

    def validate_session(self, token: str) -> Dict[str, Any]:
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")
        return payload
