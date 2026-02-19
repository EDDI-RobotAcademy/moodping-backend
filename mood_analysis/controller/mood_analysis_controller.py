"""
MoodAnalysisController — FastAPI 라우터.

Mercenary-Backend-main 의 BoardController 패턴을 따릅니다.
  - APIRouter prefix: /mood-analysis
  - 서비스는 Depends(inject_mood_analysis_service) 로 주입
  - DB 세션은 Depends(get_db) 로 주입

엔드포인트:
  POST /mood-analysis/analyze/{record_id}
      → 특정 record_id 에 대해 LLM 분석을 실행하고 결과를 저장합니다.
        (MoodRecord 가 이미 DB에 저장된 이후 호출)

  GET  /mood-analysis/{record_id}
      → 저장된 분석 결과를 조회합니다.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_optional
from app.domain.mood.models import MoodRecord
from app.domain.user.models import User
from mood_analysis.service.mood_analysis_service_impl import MoodAnalysisServiceImpl

mood_analysis_router = APIRouter(prefix="/mood-analysis", tags=["mood-analysis"])


# ------------------------------------------------------------------ #
#  의존성 주입 헬퍼                                                     #
# ------------------------------------------------------------------ #


def inject_mood_analysis_service() -> MoodAnalysisServiceImpl:
    """싱글톤 MoodAnalysisServiceImpl 인스턴스를 반환합니다."""
    return MoodAnalysisServiceImpl.get_instance()


# ------------------------------------------------------------------ #
#  엔드포인트                                                           #
# ------------------------------------------------------------------ #


@mood_analysis_router.post(
    "/analyze/{record_id}",
    summary="감정 기록 LLM 분석 실행",
    description=(
        "저장된 MoodRecord(record_id)에 대해 LLM 분석을 실행하고 "
        "결과를 mood_analysis 테이블에 저장합니다."
    ),
)
async def analyze_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
    service: MoodAnalysisServiceImpl = Depends(inject_mood_analysis_service),
):
    # MoodRecord 존재 확인
    record: MoodRecord | None = db.get(MoodRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"MoodRecord(id={record_id})를 찾을 수 없습니다.")

    # 로그인 사용자라면 본인 기록인지 검증
    if current_user and record.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="본인의 감정 기록만 분석할 수 있습니다.")

    result = await service.analyze_and_save(record=record, db=db)

    if result is None:
        raise HTTPException(
            status_code=502,
            detail="LLM 분석에 실패했습니다. 잠시 후 다시 시도해 주세요.",
        )

    return {
        "record_id": record_id,
        "analysis_text": result.analysis_text,
    }


@mood_analysis_router.get(
    "/{record_id}",
    summary="감정 분석 결과 조회",
    description="저장된 감정 분석 결과를 record_id 로 조회합니다.",
)
async def get_analysis(
    record_id: int,
    db: Session = Depends(get_db),
    service: MoodAnalysisServiceImpl = Depends(inject_mood_analysis_service),
):
    result = await service.get_analysis_by_record_id(record_id=record_id, db=db)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"record_id={record_id} 에 대한 분석 결과가 없습니다.",
        )

    return {
        "record_id": record_id,
        "analysis_text": result.analysis_text,
    }

