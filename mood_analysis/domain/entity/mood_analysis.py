"""
MoodAnalysis 도메인 엔터티.

Mercenary-Backend-main 구조를 따르며, SQLAlchemy ORM 모델과
도메인 팩토리 메서드(create)를 함께 정의합니다.

[이전 위치] app.domain.mood.models.MoodAnalysis
[현재 위치] mood_analysis.domain.entity.mood_analysis.MoodAnalysis
도메인 분리 완료 후 app.domain.mood.models 쪽 정의를 제거합니다.
"""

from sqlalchemy import BigInteger, Column, String, Text, DateTime
from sqlalchemy.sql import func

from app.database import Base


class MoodAnalysis(Base):
    """
    감정 기록(MoodRecord)에 대한 LLM 분석 결과를 저장하는 엔터티.

    Attributes:
        id            : PK (자동 증가)
        record_id     : 연관된 mood_record.id (FK 없이 논리적 참조)
        user_id       : 로그인 사용자 ID (비로그인이면 None)
        analysis_text : LLM이 생성한 감정 분석 텍스트
        created_at    : 생성 시각 (DB 서버 기준)
    """

    __tablename__ = "mood_analysis"
    # 도메인 분리 과도기: app.domain.mood.models.MoodAnalysis 와 동일 테이블
    # 양쪽 모듈이 동시에 임포트될 경우 SQLAlchemy 충돌 방지
    __table_args__ = {"extend_existing": True}

    id            = Column(BigInteger, primary_key=True, autoincrement=True)
    record_id     = Column(BigInteger, nullable=False, index=True)
    user_id       = Column(String(100), nullable=True)
    analysis_text = Column(Text, nullable=True)
    created_at    = Column(DateTime, nullable=False, server_default=func.now())

    @classmethod
    def create(
        cls,
        record_id: int,
        user_id: str | None,
        analysis_text: str,
    ) -> "MoodAnalysis":
        """
        유효성 검사를 포함한 팩토리 메서드.

        Args:
            record_id     : 연관된 MoodRecord 의 id
            user_id       : 로그인 사용자 식별자 (anon 이면 None)
            analysis_text : LLM 분석 결과 텍스트 (필수, 공백 불가)

        Returns:
            저장되지 않은 MoodAnalysis 인스턴스

        Raises:
            ValueError: analysis_text 가 비어있을 경우
        """
        if not analysis_text or not analysis_text.strip():
            raise ValueError("analysis_text must not be empty")

        return cls(
            record_id=record_id,
            user_id=user_id,
            analysis_text=analysis_text.strip(),
        )

