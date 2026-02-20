from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from event_log.domain.entity.event_log import EventLog


class EventLogRepository(ABC):
    @abstractmethod
    def save(self, session: Session, event_log: EventLog) -> EventLog:
        pass

    @abstractmethod
    def get_record_funnel(self, session: Session, threshold_minutes: int) -> dict:
        pass

    @abstractmethod
    def get_analysis_funnel(self, session: Session, threshold_minutes: int) -> dict:
        pass

    @abstractmethod
    def get_step_funnel(self, session: Session, step_names: list[str]) -> list[dict]:
        pass

    @abstractmethod
    def get_retention(self, session: Session, retention_days: int) -> dict:
        pass
