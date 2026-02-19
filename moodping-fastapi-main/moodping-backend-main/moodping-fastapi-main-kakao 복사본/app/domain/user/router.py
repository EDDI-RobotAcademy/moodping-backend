from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.domain.user.schemas import LinkDataRequest, LinkDataResponse
from app.domain.mood import service as mood_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/link-data", response_model=LinkDataResponse)
def link_anon_data(
    request: LinkDataRequest,
    db: Session = Depends(get_db),
):
    updated = mood_service.link_anon_to_user(request.user_id, request.anon_id, db)
    return LinkDataResponse(updated_count=updated)
