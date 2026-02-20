from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user_optional
from app.domain.mood.schemas import MoodRecordRequest, MoodRecordResponse
from app.domain.mood import service as mood_service
from app.domain.user.models import User

router = APIRouter(tags=["mood-records"])


@router.post("/mood-records", response_model=MoodRecordResponse)
async def create_mood_record(
    request: MoodRecordRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    authenticated_user_id = str(user.id) if user else None
    return await mood_service.save_and_analyze(request, db, authenticated_user_id)
