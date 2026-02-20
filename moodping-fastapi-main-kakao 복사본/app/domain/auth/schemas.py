from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class KakaoUserInfo(BaseModel):
    kakao_id: str
    nickname: str | None = None
    profile_image: str | None = None


class UserResponse(BaseModel):
    id: int
    kakao_id: str
    nickname: str | None = None
    profile_image: str | None = None
