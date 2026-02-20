from pydantic import BaseModel
from typing import Optional


class KakaoUserInfoResponse(BaseModel):
    id: int
    nickname: Optional[str]
    email: Optional[str]
