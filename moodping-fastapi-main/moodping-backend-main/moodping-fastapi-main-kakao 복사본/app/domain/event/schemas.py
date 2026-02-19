from pydantic import BaseModel, Field
from typing import Any


class EventLogRequest(BaseModel):
    event_id: str = Field(..., min_length=1, description="프론트에서 생성한 이벤트 UUID")
    session_id: str = Field(..., min_length=1)
    user_id: str | None = None
    anon_id: str | None = None
    event_name: str = Field(..., min_length=1)
    extra_data: dict[str, Any] | None = None


class StatusResponse(BaseModel):
    status: str = "ok"
