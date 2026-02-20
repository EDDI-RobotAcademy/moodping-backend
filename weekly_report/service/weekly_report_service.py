from abc import ABC, abstractmethod


class WeeklyReportService(ABC):

    @abstractmethod
    async def get_or_create_latest_report(self, user_id: int) -> dict:
        """
        user_id 기준 이번 주 리포트를 조회하거나,
        없으면 mood_record 7일치로 LLM 요약을 생성해 저장 후 반환한다.
        """
        pass
