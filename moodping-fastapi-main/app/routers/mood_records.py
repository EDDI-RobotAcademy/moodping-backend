from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MoodRecordRequest, MoodRecordResponse
from app.services import mood_record_service
from app.auth import get_current_user_id

router = APIRouter(tags=["mood-records"])


@router.post("/mood-records", response_model=MoodRecordResponse)
async def create_mood_record(
    request: MoodRecordRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """감정 기록 저장 + LLM 분석. 로그인 시 JWT에서 user_id 연동."""
    user_id = get_current_user_id(http_request)
    return await mood_record_service.save_and_analyze(request, db, user_id)
