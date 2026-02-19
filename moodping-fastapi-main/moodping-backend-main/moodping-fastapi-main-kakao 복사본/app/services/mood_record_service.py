import logging
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models import MoodRecord
from app.schemas import MoodRecordRequest, MoodRecordResponse
from app.services import mood_analysis_service

logger = logging.getLogger(__name__)


async def save_and_analyze(
    request: MoodRecordRequest,
    db: Session,
    authenticated_user_id: str | None = None,
) -> MoodRecordResponse:
    """
    감정 기록을 저장하고 동기적으로 LLM 분석을 실행한 뒤 통합 응답을 반환합니다.
    분석 실패 시에도 saved=True로 응답합니다.
    """
    now = datetime.now()

    record = MoodRecord(
        mood_emoji=request.mood_emoji,
        intensity=request.intensity,
        mood_text=request.mood_text,
        record_date=now.date(),
        recorded_at=now,
        user_id=authenticated_user_id,
        anon_id=None if authenticated_user_id else request.anon_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("감정 기록 저장 완료. record_id=%s, intensity=%s", record.id, record.intensity)

    analysis_result = await mood_analysis_service.analyze_and_save(record, db)
    status = "success" if analysis_result else "failed"
    logger.info("분석 완료. record_id=%s, status=%s", record.id, status)

    return MoodRecordResponse(
        record_id=record.id,
        record_date=record.record_date,
        saved=True,
        analysis=analysis_result,
        analysis_status=status,
    )


def link_anon_to_user(user_id: str, anon_id: str, db: Session) -> int:
    """anon_id로 저장된 기록을 실제 user_id로 연동합니다."""
    updated = (
        db.query(MoodRecord)
        .filter(MoodRecord.anon_id == anon_id, MoodRecord.user_id.is_(None))
        .update({"user_id": user_id, "anon_id": None}, synchronize_session=False)
    )
    db.commit()
    logger.info("anon→user 연동. user_id=%s, anon_id=%s, rows=%s", user_id, anon_id, updated)
    return updated
