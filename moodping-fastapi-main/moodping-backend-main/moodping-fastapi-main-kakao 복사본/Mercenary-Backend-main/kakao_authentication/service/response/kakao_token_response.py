from pydantic import BaseModel


class KakaoTokenResponse(BaseModel):
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str | None = None
    refresh_token_expires_in: int | None = None
    scope: str | None = None
