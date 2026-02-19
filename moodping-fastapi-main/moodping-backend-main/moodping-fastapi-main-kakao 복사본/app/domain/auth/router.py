import logging
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import get_settings
from app.deps import get_current_user
from app.domain.auth import service as auth_service
from app.domain.auth.schemas import UserResponse
from app.domain.user.models import User

router = APIRouter(prefix="/auth", tags=["auth"])
kakao_redirect_router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"


@router.get("/kakao")
def kakao_login():
    settings = get_settings()
    if not settings.kakao_client_id:
        raise HTTPException(status_code=500, detail="KAKAO_CLIENT_ID가 설정되지 않았습니다.")
    params = urlencode({
        "client_id": settings.kakao_client_id,
        "redirect_uri": settings.kakao_redirect_uri,
        "response_type": "code",
    })
    return RedirectResponse(url=f"{KAKAO_AUTH_URL}?{params}")


@router.get("/callback")
@router.get("/kakao/callback")
async def kakao_callback(
    code: str = Query(...),
    db: Session = Depends(get_db),
):
    kakao_token = await auth_service.get_kakao_access_token(code)
    if not kakao_token:
        raise HTTPException(status_code=400, detail="카카오 토큰 발급 실패")

    kakao_user = await auth_service.get_kakao_user_info(kakao_token)
    if not kakao_user:
        raise HTTPException(status_code=400, detail="카카오 사용자 정보 조회 실패")

    user = auth_service.upsert_user(kakao_user, db)
    jwt_token = auth_service.generate_jwt(user)

    logger.info("카카오 로그인 성공. user_id=%s, nickname=%s", user.id, user.nickname)
    return RedirectResponse(url=f"/?token={jwt_token}")


@kakao_redirect_router.get("/kakao-authentication/request-access-token-after-redirection")
async def kakao_redirect_callback(
    code: str = Query(...),
    db: Session = Depends(get_db),
):
    return await kakao_callback(code=code, db=db)


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        kakao_id=user.kakao_id,
        nickname=user.nickname,
        profile_image=user.profile_image,
    )
