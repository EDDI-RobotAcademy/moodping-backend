import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.database import SessionLocal
from event_log.domain.entity.event_log import EventLog
from event_log.repository.event_log_repository_impl import (
    EventLogRepositoryImpl,
    FUNNEL_STEPS,
)
from event_log.controller.request.create_event_log_request import CreateEventLogRequest
from event_log.service.event_log_service import EventLogService

logger = logging.getLogger(__name__)

DROP_THRESHOLD_MINUTES = 10
RETENTION_DAYS = 7


class EventLogServiceImpl(EventLogService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        self.event_log_repository = EventLogRepositoryImpl.get_instance()

    def create(self, request: CreateEventLogRequest) -> EventLog:
        session: Session = SessionLocal()
        try:
            event_log = EventLog.create(
                event_id=request.event_id,
                session_id=request.session_id,
                event_name=request.event_name,
                user_id=request.user_id,
                anon_id=request.anon_id,
                extra_data=request.extra_data,
                occurred_at=datetime.utcnow(),
            )
            self.event_log_repository.save(session, event_log)
            session.commit()
            logger.debug(
                "이벤트 저장. event_name=%s, session_id=%s",
                request.event_name,
                request.session_id,
            )
            return event_log
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_metrics(self) -> dict:
        session: Session = SessionLocal()
        try:
            record_funnel = self.event_log_repository.get_record_funnel(
                session, DROP_THRESHOLD_MINUTES
            )
            analysis_funnel = self.event_log_repository.get_analysis_funnel(
                session, DROP_THRESHOLD_MINUTES
            )
            step_funnel = self.event_log_repository.get_step_funnel(
                session, FUNNEL_STEPS
            )
            retention = self.event_log_repository.get_retention(
                session, RETENTION_DAYS
            )

            return {
                "drop_threshold_minutes": DROP_THRESHOLD_MINUTES,
                "funnel": {
                    "record_funnel": record_funnel,
                    "analysis_funnel": analysis_funnel,
                },
                "step_funnel": step_funnel,
                "retention": retention,
            }
        finally:
            session.close()
