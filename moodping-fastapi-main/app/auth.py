"""JWT 기반 인증 (카카오 로그인 세션)."""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Request
from app.config import get_settings


def create_access_token(user_id: str, nickname: str) -> str:
    settings = get_settings()
    payload = {
        "sub": user_id,
        "nickname": nickname,
        "exp": datetime.utcnow() + timedelta(days=settings.jwt_expire_days),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None


COOKIE_NAME = "moodping_token"


def get_current_user_id(request: Request) -> Optional[str]:
    """쿠키에서 JWT 검증 후 user_id 반환."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    payload = decode_token(token)
    return str(payload["sub"]) if payload and "sub" in payload else None
