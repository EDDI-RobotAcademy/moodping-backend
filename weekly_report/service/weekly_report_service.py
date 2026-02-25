from abc import ABC, abstractmethod

class WeeklyReportService(ABC):
    @abstractmethod
    async def get_or_create_latest_report(self, user_id: int) -> dict:
        pass
