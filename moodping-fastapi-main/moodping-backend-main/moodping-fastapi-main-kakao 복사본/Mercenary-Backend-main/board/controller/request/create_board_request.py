from pydantic import BaseModel


class CreateBoardRequest(BaseModel):
    title: str
    content: str
