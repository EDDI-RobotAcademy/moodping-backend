from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import debug_service

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/recent-records")
def get_recent_records(db: Session = Depends(get_db)):
    """
    최근 감정 기록 10건 조회 (anon_id, emoji, intensity, mood_text, analysis_text 포함).
    팀원 시각화용 디버그 대시보드 API.
    """
    return debug_service.get_recent_records(db)


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """
    10분 임계값 기반 퍼널 이탈률 + 평균 소요 시간 + 7일 리텐션 지표.
    팀원 시각화용 디버그 대시보드 API.
    """
    return debug_service.get_metrics(db)
