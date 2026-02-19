from pydantic import BaseModel, Field


class LinkDataRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    anon_id: str = Field(..., min_length=1)


class LinkDataResponse(BaseModel):
    updated_count: int
