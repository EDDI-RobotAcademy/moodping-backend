"""
MoodAnalysisServiceImpl — MoodAnalysisService 구현체.

핵심 책임:
  1. llm/factory.get_llm_client() 를 통해 LLM 클라이언트를 주입받아 재사용
  2. mood_analysis/prompt/mood_analysis_prompt 로 프롬프트를 빌드
  3. LLM 응답을 파싱하여 MoodAnalysis 엔터티 생성 → Repository 를 통해 저장
  4. Mercenary-Backend-main 의 싱글톤(get_instance) 패턴 적용

의존성: MP-02 완료 후 (llm 모듈 사용 가능 전제)
"""

import json
import logging
import re

from sqlalchemy.orm import Session

from app.domain.mood.models import MoodRecord
from app.domain.mood.schemas import AnalysisResult
from app.llm.factory import get_llm_client                      # MP-02 핵심 재사용
from mood_analysis.domain.entity.mood_analysis import MoodAnalysis
from mood_analysis.prompt import mood_analysis_prompt
from mood_analysis.repository.mood_analysis_repository_impl import (
    MoodAnalysisRepositoryImpl,
)
from mood_analysis.service.mood_analysis_service import MoodAnalysisService

logger = logging.getLogger(__name__)

# LLM 응답의 analysis_text 최대 글자 수 (토큰 초과 방어)
_MAX_ANALYSIS_CHARS = 1500


class MoodAnalysisServiceImpl(MoodAnalysisService):
    """
    LLM 호출 → 응답 파싱 → DB 저장의 전체 흐름을 담당합니다.

    싱글톤: get_instance() 로 인스턴스를 획득합니다.
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls) -> "MoodAnalysisServiceImpl":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        # 중복 초기화 방지 (싱글톤 보호)
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.mood_analysis_repository = MoodAnalysisRepositoryImpl.get_instance()

    # ------------------------------------------------------------------ #
    #  공개 API                                                            #
    # ------------------------------------------------------------------ #

    async def analyze_and_save(
        self,
        record: MoodRecord,
        db: Session,
    ) -> AnalysisResult | None:
        """
        LLM 분석을 실행하고 mood_analysis 테이블에 저장합니다.
        실패 시 None 을 반환합니다 (MoodRecord 저장은 이미 완료된 상태).

        Steps:
            1. llm/factory.get_llm_client() 로 LLM 클라이언트 획득
            2. mood_analysis_prompt.build(record) 로 유저 프롬프트 생성
            3. LLM 응답 → _parse_analysis_text() 로 파싱
            4. MoodAnalysis.create() 팩토리 메서드로 엔터티 생성
            5. MoodAnalysisRepository.save() 로 DB 저장
        """
        llm = get_llm_client()
        system_prompt = mood_analysis_prompt.SYSTEM_PROMPT
        user_prompt   = mood_analysis_prompt.build(record)

        raw = await llm.complete(system_prompt, user_prompt)
        if not raw:
            logger.error(
                "[MoodAnalysisService] LLM 응답 없음 — 타임아웃 또는 API 오류 "
                "(record_id=%s)", record.id
            )
            return None

        logger.info(
            "[MoodAnalysisService] LLM 원본 응답 길이: %d chars (record_id=%s)",
            len(raw), record.id,
        )
        logger.debug("[MoodAnalysisService] LLM 원본 응답 앞 200자: %s", raw[:200])

        analysis_text = self._parse_analysis_text(raw)
        if not analysis_text:
            logger.warning(
                "[MoodAnalysisService] LLM 응답 파싱 실패 (record_id=%s)", record.id
            )
            return None

        owner_id = record.user_id or record.anon_id

        try:
            analysis = MoodAnalysis.create(
                record_id=record.id,
                user_id=owner_id,
                analysis_text=analysis_text,
            )
            self.mood_analysis_repository.save(db, analysis)
            db.commit()
            logger.info(
                "[MoodAnalysisService] 분석 결과 저장 완료 (record_id=%s)", record.id
            )
            return AnalysisResult(analysis_text=analysis_text)

        except Exception as exc:
            db.rollback()
            logger.error(
                "[MoodAnalysisService] DB 저장 실패 (record_id=%s): %s",
                record.id, exc,
            )
            return None

    async def get_analysis_by_record_id(
        self,
        record_id: int,
        db: Session,
    ) -> AnalysisResult | None:
        """저장된 분석 결과를 record_id 로 조회합니다."""
        analysis = self.mood_analysis_repository.find_by_record_id(db, record_id)
        if not analysis or not analysis.analysis_text:
            return None
        return AnalysisResult(analysis_text=analysis.analysis_text)

    # ------------------------------------------------------------------ #
    #  내부 헬퍼                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
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
            text = (
                raw.replace("\\n", "\n")
                   .replace('\\"', '"')
                   .replace("\\\\", "\\")
            )
            return text[:_MAX_ANALYSIS_CHARS] if text.strip() else None

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

            return text[:_MAX_ANALYSIS_CHARS] if text.strip() else None

        except (json.JSONDecodeError, AttributeError):
            logger.warning(
                "[MoodAnalysisService] analysis_text 파싱 최종 실패 — raw 반환"
            )
            return content[:_MAX_ANALYSIS_CHARS]

