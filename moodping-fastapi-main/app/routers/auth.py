"""카카오 OAuth 2.0 로그인."""
import logging
import os
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.auth import create_access_token, COOKIE_NAME, decode_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_ME_URL = "https://kapi.kakao.com/v2/user/me"


def _redirect_uri(request: Request) -> str:
    base = str(request.base_url).rstrip("/")
    if "0.0.0.0" in base:
        base = base.replace("0.0.0.0", "localhost")
    return f"{base}/auth/kakao/callback"


def _get_client_id() -> str:
    key = get_settings().kakao_rest_api_key or os.environ.get("KAKAO_REST_API_KEY") or ""
    return (key or "").strip()


@router.get("/kakao", include_in_schema=False)
def kakao_login(request: Request):
    client_id = _get_client_id()
    if not client_id:
        return RedirectResponse(url="/?error=kakao_not_configured", status_code=302)
    params = {
        "client_id": client_id,
        "redirect_uri": _redirect_uri(request),
        "response_type": "code",
    }
    return RedirectResponse(url=f"{KAKAO_AUTH_URL}?{urlencode(params)}", status_code=302)


@router.get("/kakao/callback", include_in_schema=False)
async def kakao_callback(request: Request, code: Optional[str] = None):
    if not code:
        return RedirectResponse(url="/?error=no_code", status_code=302)

    redirect_uri = _redirect_uri(request)
    settings = get_settings()
    client_id = _get_client_id()
    if not client_id:
        return RedirectResponse(url="/?error=kakao_not_configured", status_code=302)

    async with httpx.AsyncClient() as client:
        token_data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        if settings.kakao_client_secret:
            token_data["client_secret"] = settings.kakao_client_secret

        token_res = await client.post(
            KAKAO_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=token_data,
        )
        if token_res.status_code != 200:
            logger.warning("카카오 토큰 실패: %s", token_res.status_code)
            return RedirectResponse(url="/?error=token_failed", status_code=302)

        access_token = token_res.json().get("access_token")
        if not access_token:
            return RedirectResponse(url="/?error=no_token", status_code=302)

        user_res = await client.get(
            KAKAO_USER_ME_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_res.status_code != 200:
            return RedirectResponse(url="/?error=user_failed", status_code=302)

        user = user_res.json()
        kakao_id = str(user.get("id", ""))
        nickname = "카카오사용자"
        account = user.get("kakao_account") or {}
        profile = account.get("profile") or {}
        if isinstance(profile, dict) and profile.get("nickname"):
            nickname = profile["nickname"]

    jwt_token = create_access_token(user_id=kakao_id, nickname=nickname)
    resp = RedirectResponse(url="/", status_code=302)
    resp.set_cookie(
        key=COOKIE_NAME,
        value=jwt_token,
        max_age=settings.jwt_expire_days * 24 * 3600,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return resp


@router.get("/me")
def auth_me(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return {"logged_in": False, "user_id": None, "nickname": None}
    payload = decode_token(token)
    if not payload:
        return {"logged_in": False, "user_id": None, "nickname": None}
    return {
        "logged_in": True,
        "user_id": payload.get("sub"),
        "nickname": payload.get("nickname") or "사용자",
    }


@router.get("/logout", include_in_schema=False)
def logout():
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie(key=COOKIE_NAME, path="/")
    return resp
