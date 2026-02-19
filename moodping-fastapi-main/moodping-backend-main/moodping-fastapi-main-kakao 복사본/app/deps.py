from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.auth.jwt import decode_access_token
from app.domain.user.models import User


def _extract_token(authorization: str | None = Header(None)) -> str | None:
    if not authorization:
        return None
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization


def get_current_user_optional(
    token: str | None = Depends(_extract_token),
    db: Session = Depends(get_db),
) -> User | None:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(User).filter(User.id == int(user_id)).first()


def get_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return user
