from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.domain.event.schemas import EventLogRequest, StatusResponse
from app.domain.event import service as event_service

router = APIRouter(tags=["events"])


@router.post("/api/events", response_model=StatusResponse)
def log_event(
    request: EventLogRequest,
    db: Session = Depends(get_db),
):
    event_service.save(request, db)
    return StatusResponse()


@router.get("/api/debug/recent-records", tags=["debug"])
def get_recent_records(db: Session = Depends(get_db)):
    return event_service.get_recent_records(db)


@router.get("/api/debug/metrics", tags=["debug"])
def get_metrics(db: Session = Depends(get_db)):
    return event_service.get_metrics(db)
