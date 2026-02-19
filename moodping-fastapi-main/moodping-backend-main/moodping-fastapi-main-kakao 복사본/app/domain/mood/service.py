import json
import logging
import re
from datetime import datetime
from sqlalchemy.orm import Session

from app.domain.mood.models import MoodRecord, MoodAnalysis
from app.domain.mood.schemas import MoodRecordRequest, MoodRecordResponse, AnalysisResult
from app.llm.factory import get_llm_client
from app.prompt import mood_analysis_prompt

logger = logging.getLogger(__name__)

MAX_ANALYSIS_CHARS = 1500


async def save_and_analyze(
    request: MoodRecordRequest,
    db: Session,
    authenticated_user_id: str | None = None,
) -> MoodRecordResponse:
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

    analysis_result = await _analyze_and_save(record, db)
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
    updated = (
        db.query(MoodRecord)
        .filter(MoodRecord.anon_id == anon_id, MoodRecord.user_id.is_(None))
        .update({"user_id": user_id, "anon_id": None}, synchronize_session=False)
    )
    db.commit()
    logger.info("anon→user 연동. user_id=%s, anon_id=%s, rows=%s", user_id, anon_id, updated)
    return updated


async def _analyze_and_save(record: MoodRecord, db: Session) -> AnalysisResult | None:
    llm = get_llm_client()
    system_prompt = mood_analysis_prompt.SYSTEM_PROMPT
    user_prompt = mood_analysis_prompt.build(record)

    raw = await llm.complete(system_prompt, user_prompt)
    if not raw:
        logger.error("LLM 응답 없음 (None 반환) — 타임아웃 또는 API 오류")
        return None

    logger.info("LLM 원본 응답 길이: %d chars", len(raw))

    analysis_text = _parse_analysis_text(raw)
    if not analysis_text:
        return None

    owner_id = record.user_id or record.anon_id
    analysis = MoodAnalysis(
        record_id=record.id,
        user_id=owner_id,
        analysis_text=analysis_text,
    )
    db.add(analysis)
    db.commit()

    return AnalysisResult(analysis_text=analysis_text)


def _parse_analysis_text(content: str) -> str | None:
    if not content:
        return None

    match = re.search(
        r'"analysis_text"\s*:\s*"((?:[^"\\]|\\.)*)"',
        content,
        re.DOTALL,
    )
    if not match:
        match = re.search(
            r'"analysis_text"\s*:\s*"((?:[^"\\]|\\.)*)',
            content,
            re.DOTALL,
        )
    if match:
        raw = match.group(1)
        text = raw.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
        return text[:MAX_ANALYSIS_CHARS] if text.strip() else None

    try:
        cleaned = re.sub(r"```(?:json)?\s*", "", content, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE).strip()
        data = json.loads(cleaned)
        text = data.get("analysis_text", "")

        if text and text.strip().startswith("{"):
            try:
                inner = json.loads(text)
                text = inner.get("analysis_text", text)
            except (json.JSONDecodeError, AttributeError):
                pass

        return text[:MAX_ANALYSIS_CHARS] if text.strip() else None

    except (json.JSONDecodeError, AttributeError):
        logger.warning("analysis_text 파싱 최종 실패 — raw 반환")
        return content[:MAX_ANALYSIS_CHARS]
