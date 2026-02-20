from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import EventLogRequest, StatusResponse
from app.services import event_log_service

router = APIRouter(prefix="/api", tags=["events"])


@router.post("/events", response_model=StatusResponse)
def log_event(
    request: EventLogRequest,
    db: Session = Depends(get_db),
):
    """
    프론트엔드의 유저 퍼널 이벤트를 저장합니다.
    event_id UNIQUE 제약으로 중복 저장이 방지됩니다.
    """
    event_log_service.save(request, db)
    return StatusResponse()
