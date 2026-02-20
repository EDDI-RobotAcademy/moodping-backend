from datetime import date

from sqlalchemy.orm import Session

from weekly_report.domain.entity.weekly_report import WeeklyReport
from weekly_report.repository.weekly_report_repository import WeeklyReportRepository


class WeeklyReportRepositoryImpl(WeeklyReportRepository):

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls) -> "WeeklyReportRepositoryImpl":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def find_by_user_and_week(
        self,
        session: Session,
        user_id: int,
        week_start: date,
    ) -> WeeklyReport | None:
        return (
            session.query(WeeklyReport)
            .filter(
                WeeklyReport.user_id == user_id,
                WeeklyReport.week_start == week_start,
            )
            .first()
        )

    def save(self, session: Session, report: WeeklyReport) -> WeeklyReport:
        session.add(report)
        return report
