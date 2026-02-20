from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from event_log.domain.entity.event_log import EventLog

if TYPE_CHECKING:
    from event_log.controller.request.create_event_log_request import CreateEventLogRequest


class EventLogService(ABC):
    @abstractmethod
    def create(self, request: "CreateEventLogRequest") -> EventLog:
        pass

    @abstractmethod
    def get_metrics(self) -> dict:
        pass
