from pydantic import BaseModel
from typing import Optional


class KakaoLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

    user_id: int
    nickname: Optional[str]
    email: Optional[str]
