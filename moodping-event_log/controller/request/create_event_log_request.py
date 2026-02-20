from typing import Any

from pydantic import BaseModel, Field


class CreateEventLogRequest(BaseModel):
    """이벤트 로그 생성 요청"""

    event_id: str = Field(..., min_length=1, description="프론트에서 생성한 이벤트 UUID")
    session_id: str = Field(..., min_length=1)
    user_id: str | None = None
    anon_id: str | None = None
    event_name: str = Field(..., min_length=1)
    extra_data: dict[str, Any] | None = None
