"""
MoodAnalysisRepositoryImpl — MoodAnalysisRepository 구현체.

Mercenary-Backend-main 의 BoardRepositoryImpl 싱글톤 패턴을 따릅니다.
  - __new__ + get_instance() 로 프로세스 전역 단일 인스턴스 보장
  - 세션 관리는 서비스 계층에 위임 (Repository 는 session 을 직접 생성하지 않음)
"""

from sqlalchemy.orm import Session

from mood_analysis.domain.entity.mood_analysis import MoodAnalysis
from mood_analysis.repository.mood_analysis_repository import MoodAnalysisRepository


class MoodAnalysisRepositoryImpl(MoodAnalysisRepository):

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls) -> "MoodAnalysisRepositoryImpl":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    # ------------------------------------------------------------------ #
    #  쓰기                                                                #
    # ------------------------------------------------------------------ #

    def save(self, session: Session, analysis: MoodAnalysis) -> MoodAnalysis:
        """
        MoodAnalysis 엔터티를 세션에 추가합니다.
        commit / rollback 은 서비스 계층이 담당합니다.
        """
        session.add(analysis)
        return analysis

    # ------------------------------------------------------------------ #
    #  읽기                                                                #
    # ------------------------------------------------------------------ #

    def find_by_record_id(
        self, session: Session, record_id: int
    ) -> MoodAnalysis | None:
        """record_id 로 분석 결과 단건 조회 (없으면 None)."""
        return (
            session.query(MoodAnalysis)
            .filter(MoodAnalysis.record_id == record_id)
            .first()
        )

    def find_all_by_user_id(
        self, session: Session, user_id: str
    ) -> list[MoodAnalysis]:
        """user_id 에 속한 모든 분석 결과를 최신순으로 반환합니다."""
        return (
            session.query(MoodAnalysis)
            .filter(MoodAnalysis.user_id == user_id)
            .order_by(MoodAnalysis.created_at.desc())
            .all()
        )

    def exists_by_record_id(self, session: Session, record_id: int) -> bool:
        """중복 분석 방지용 존재 여부 확인."""
        return (
            session.query(MoodAnalysis)
            .filter(MoodAnalysis.record_id == record_id)
            .count()
        ) > 0

