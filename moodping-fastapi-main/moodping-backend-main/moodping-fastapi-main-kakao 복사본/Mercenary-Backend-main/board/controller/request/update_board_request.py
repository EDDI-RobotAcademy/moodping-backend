from pydantic import BaseModel

class UpdateBoardRequest(BaseModel):
    title: str | None = None
    content: str | None = None
