"""
MoodAnalysisService — 추상 베이스 클래스 (ABC).

핵심 메서드:
  - analyze_and_save(record, db) → LLM 호출 후 DB 저장

Mercenary-Backend-main 의 BoardService 패턴을 따릅니다.
"""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.domain.mood.models import MoodRecord
from app.domain.mood.schemas import AnalysisResult


class MoodAnalysisService(ABC):

    @abstractmethod
    async def analyze_and_save(
        self,
        record: MoodRecord,
        db: Session,
    ) -> AnalysisResult | None:
        """
        MoodRecord 를 받아 LLM 분석을 실행하고,
        결과를 mood_analysis 테이블에 저장한 뒤 AnalysisResult 를 반환합니다.

        Args:
            record : 분석 대상 MoodRecord 엔터티 (이미 DB에 저장된 상태)
            db     : 활성 SQLAlchemy 세션

        Returns:
            AnalysisResult(analysis_text=...) 또는 실패 시 None
        """
        pass

    @abstractmethod
    async def get_analysis_by_record_id(
        self,
        record_id: int,
        db: Session,
    ) -> AnalysisResult | None:
        """
        기존에 저장된 분석 결과를 record_id 로 조회합니다.

        Returns:
            저장된 AnalysisResult 또는 존재하지 않으면 None
        """
        pass

