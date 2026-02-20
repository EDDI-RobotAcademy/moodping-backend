from fastapi import APIRouter, Depends, HTTPException

from event_log.controller.request.create_event_log_request import CreateEventLogRequest
from event_log.service.event_log_service_impl import EventLogServiceImpl

event_log_router = APIRouter(prefix="/event-log", tags=["event_log"])


def inject_event_log_service() -> EventLogServiceImpl:
    return EventLogServiceImpl.get_instance()


@event_log_router.post("/create")
def create_event_log(
    request: CreateEventLogRequest,
    event_log_service: EventLogServiceImpl = Depends(inject_event_log_service),
):
    """이벤트 로그를 저장합니다. event_id UNIQUE 제약으로 중복 저장이 방지됩니다."""
    try:
        event_log = event_log_service.create(request)
        return {
            "id": event_log.id,
            "event_id": event_log.event_id,
            "event_name": event_log.event_name,
            "status": "ok",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@event_log_router.get("/metrics")
def get_event_log_metrics(
    event_log_service: EventLogServiceImpl = Depends(inject_event_log_service),
):
    """이벤트 퍼널 및 리텐션 메트릭을 반환합니다."""
    return event_log_service.get_metrics()
