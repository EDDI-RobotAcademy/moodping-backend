from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LinkDataRequest, LinkDataResponse
from app.services import mood_record_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/link-data", response_model=LinkDataResponse)
def link_anon_data(
    request: LinkDataRequest,
    db: Session = Depends(get_db),
):
    """
    비로그인(anon_id) 상태로 저장된 감정 기록을
    회원가입/로그인 후 실제 계정(user_id)에 연동합니다.
    """
    updated = mood_record_service.link_anon_to_user(request.user_id, request.anon_id, db)
    return LinkDataResponse(updated_count=updated)
