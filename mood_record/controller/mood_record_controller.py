import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from moodping.mood_record.controller.request.create_mood_record_request import CreateMoodRecordRequest
from moodping.mood_record.service.mood_record_service_impl import MoodRecordServiceImpl
from moodping.mood_analysis.service.mood_analysis_service_impl import MoodAnalysisServiceImpl
from moodping.authentication.controller.authentication_controller import get_current_user_payload_optional
from moodping.config.mysql_config import get_db

logger = logging.getLogger(__name__)

mood_record_router = APIRouter(tags=["mood-records"])


def inject_mood_record_service() -> MoodRecordServiceImpl:
    return MoodRecordServiceImpl.get_instance()


def inject_mood_analysis_service() -> MoodAnalysisServiceImpl:
    return MoodAnalysisServiceImpl.get_instance()


@mood_record_router.post("/mood-records")
async def create_mood_record(
    request: CreateMoodRecordRequest,
    db: Session = Depends(get_db),
    mood_record_service: MoodRecordServiceImpl = Depends(inject_mood_record_service),
    mood_analysis_service: MoodAnalysisServiceImpl = Depends(inject_mood_analysis_service),
    payload: dict | None = Depends(get_current_user_payload_optional),
):
    try:
        user_id = payload.get("sub") if payload else None
        record = mood_record_service.create(
            mood_emoji=request.mood_emoji,
            intensity=request.intensity,
            mood_text=request.mood_text,
            user_id=user_id,
            anon_id=request.anon_id if not user_id else None,
        )

        analysis_result = await mood_analysis_service.analyze_and_save(record=record, db=db)
        analysis_text = analysis_result.analysis_text if analysis_result else None
        analysis_status = "success" if analysis_result else "failed"

        return {
            "record_id": record.id,
            "record_date": record.record_date.isoformat(),
            "saved": True,
            "analysis": {"analysis_text": analysis_text} if analysis_text else None,
            "analysis_status": analysis_status,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
