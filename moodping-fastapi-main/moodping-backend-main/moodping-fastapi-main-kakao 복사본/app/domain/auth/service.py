import logging
import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.domain.user.models import User
from app.domain.auth.schemas import KakaoUserInfo
from app.domain.auth.jwt import create_access_token

logger = logging.getLogger(__name__)

KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


async def get_kakao_access_token(code: str) -> str | None:
    settings = get_settings()
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.kakao_client_id,
        "redirect_uri": settings.kakao_redirect_uri,
        "code": code,
    }
    if settings.kakao_client_secret:
        data["client_secret"] = settings.kakao_client_secret
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            KAKAO_TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        )
    if resp.status_code != 200:
        logger.error("카카오 토큰 요청 실패: %s %s", resp.status_code, resp.text)
        return None
    return resp.json().get("access_token")


async def get_kakao_user_info(access_token: str) -> KakaoUserInfo | None:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            KAKAO_USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if resp.status_code != 200:
        logger.error("카카오 유저 정보 요청 실패: %s %s", resp.status_code, resp.text)
        return None

    data = resp.json()
    kakao_id = str(data["id"])
    properties = data.get("properties", {})
    return KakaoUserInfo(
        kakao_id=kakao_id,
        nickname=properties.get("nickname"),
        profile_image=properties.get("profile_image"),
    )


def upsert_user(kakao_info: KakaoUserInfo, db: Session) -> User:
    user = db.query(User).filter(User.kakao_id == kakao_info.kakao_id).first()
    if user:
        user.nickname = kakao_info.nickname
        user.profile_image = kakao_info.profile_image
    else:
        user = User(
            kakao_id=kakao_info.kakao_id,
            nickname=kakao_info.nickname,
            profile_image=kakao_info.profile_image,
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def generate_jwt(user: User) -> str:
    return create_access_token(user.id, user.kakao_id)
