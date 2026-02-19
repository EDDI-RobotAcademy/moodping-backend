"""
MoodAnalysisRepository — 추상 베이스 클래스 (ABC).

Mercenary-Backend-main 의 BoardRepository 패턴을 따릅니다.
구현체(Impl)는 mood_analysis_repository_impl.py 에 정의됩니다.
"""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from mood_analysis.domain.entity.mood_analysis import MoodAnalysis


class MoodAnalysisRepository(ABC):

    @abstractmethod
    def save(self, session: Session, analysis: MoodAnalysis) -> MoodAnalysis:
        """분석 결과를 세션에 추가하고 반환합니다."""
        pass

    @abstractmethod
    def find_by_record_id(
        self, session: Session, record_id: int
    ) -> MoodAnalysis | None:
        """특정 mood_record_id 에 연결된 분석 결과를 조회합니다."""
        pass

    @abstractmethod
    def find_all_by_user_id(
        self, session: Session, user_id: str
    ) -> list[MoodAnalysis]:
        """특정 사용자의 모든 분석 결과를 최신순으로 조회합니다."""
        pass

    @abstractmethod
    def exists_by_record_id(self, session: Session, record_id: int) -> bool:
        """해당 record_id 에 대한 분석 결과가 이미 존재하는지 확인합니다."""
        pass

