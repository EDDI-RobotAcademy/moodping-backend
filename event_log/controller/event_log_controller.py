from fastapi import APIRouter, Depends, HTTPException
from moodping.event_log.controller.request.create_event_log_request import CreateEventLogRequest
from moodping.event_log.service.event_log_service_impl import EventLogServiceImpl

event_log_router = APIRouter(tags=["events"])


def inject_event_log_service() -> EventLogServiceImpl:
    return EventLogServiceImpl.get_instance()


@event_log_router.post("/api/events")
def log_event(
    request: CreateEventLogRequest,
    event_log_service: EventLogServiceImpl = Depends(inject_event_log_service),
):
    try:
        event_log_service.create(request)
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@event_log_router.get("/api/debug/recent-records", tags=["debug"])
def get_recent_records(
    event_log_service: EventLogServiceImpl = Depends(inject_event_log_service),
):
    return event_log_service.get_recent_records()


@event_log_router.get("/api/debug/metrics", tags=["debug"])
def get_metrics(
    event_log_service: EventLogServiceImpl = Depends(inject_event_log_service),
):
    return event_log_service.get_metrics()
