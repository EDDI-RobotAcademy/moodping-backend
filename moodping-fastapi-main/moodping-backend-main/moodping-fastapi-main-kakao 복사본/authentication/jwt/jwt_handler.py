"""
JWT 생성/검증.
비즈니스 규칙: 만료 7일(10080분), Payload: sub(user_id), kakao_id, exp
"""
from datetime import datetime, timedelta, timezone

import jwt

from app.config import get_settings

JWT_EXPIRE_MINUTES = 10080  # 7일


def create_access_token(user_id: int, kakao_id: str) -> str:
    settings = get_settings()
    expire_minutes = getattr(settings, "jwt_expire_minutes", JWT_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {
        "sub": str(user_id),
        "kakao_id": kakao_id,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError:
        return None
