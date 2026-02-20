from abc import ABC, abstractmethod
from datetime import date

from sqlalchemy.orm import Session

from weekly_report.domain.entity.weekly_report import WeeklyReport


class WeeklyReportRepository(ABC):

    @abstractmethod
    def find_by_user_and_week(
        self,
        session: Session,
        user_id: int,
        week_start: date,
    ) -> WeeklyReport | None:
        pass

    @abstractmethod
    def save(self, session: Session, report: WeeklyReport) -> WeeklyReport:
        pass
