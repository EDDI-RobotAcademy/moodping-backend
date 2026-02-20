from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MoodRecordRequest, MoodRecordResponse
from app.services import mood_record_service

router = APIRouter(tags=["mood-records"])


@router.post("/mood-records", response_model=MoodRecordResponse)
async def create_mood_record(
    request: MoodRecordRequest,
    db: Session = Depends(get_db),
):
    """
    감정 기록 저장 + LLM 분석을 동기적으로 처리하여 통합 응답을 반환합니다.

    - 인증 미구현 상태: authenticated_user_id=None (비로그인 처리)
    - 추후 JWT 토큰 파싱 후 주입하는 방식으로 확장 가능
    """
    authenticated_user_id = None  # TODO: JWT 구현 시 토큰에서 추출
    return await mood_record_service.save_and_analyze(request, db, authenticated_user_id)
