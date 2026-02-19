import json
import logging
import re
from sqlalchemy.orm import Session
from app.models import MoodRecord, MoodAnalysis
from app.schemas import AnalysisResult
from app.llm.factory import get_llm_client
from app.prompt import mood_analysis_prompt

logger = logging.getLogger(__name__)


async def analyze_and_save(record: MoodRecord, db: Session) -> AnalysisResult | None:
    """
    LLM 분석을 실행하고 mood_analysis 테이블에 저장합니다.
    실패 시 None을 반환합니다 (기록 저장은 이미 완료된 상태).
    """
    llm = get_llm_client()
    system_prompt = mood_analysis_prompt.SYSTEM_PROMPT
    user_prompt = mood_analysis_prompt.build(record)

    raw = await llm.complete(system_prompt, user_prompt)
    if not raw:
        logger.error("LLM 응답 없음 (None 반환) — 타임아웃 또는 API 오류")
        return None

    logger.info("LLM 원본 응답 길이: %d chars", len(raw))
    logger.info("LLM 원본 응답 앞 200자: %s", raw[:200])

    analysis_text = _parse_analysis_text(raw)
    logger.info("파싱 결과 길이: %s chars", len(analysis_text) if analysis_text else 0)
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


MAX_ANALYSIS_CHARS = 1500


def _parse_analysis_text(content: str) -> str | None:
    """
    LLM 응답에서 analysis_text 값을 추출합니다.

    우선순위:
    1) 정규식으로 "analysis_text": "..." 값 직접 추출 (가장 강건)
    2) 마크다운 코드 블록 제거 후 JSON 파싱
    3) 중첩 JSON 방어
    """
    if not content:
        return None

    # 1) 정규식으로 직접 추출 — 완전한 JSON 우선, 잘린 JSON도 처리
    # 1-a) 닫는 따옴표가 있는 정상 케이스
    match = re.search(
        r'"analysis_text"\s*:\s*"((?:[^"\\]|\\.)*)"',
        content,
        re.DOTALL,
    )
    # 1-b) 토큰 초과로 잘린 케이스 (닫는 따옴표 없음)
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

    # 2) 코드 블록 제거 후 JSON 파싱
    try:
        cleaned = re.sub(r"```(?:json)?\s*", "", content, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE).strip()
        data = json.loads(cleaned)
        text = data.get("analysis_text", "")

        # 중첩 JSON 방어
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
