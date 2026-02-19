import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import EventLog
from app.schemas import EventLogRequest

logger = logging.getLogger(__name__)


def save(request: EventLogRequest, db: Session) -> None:
    """이벤트 로그를 저장합니다. event_id UNIQUE 제약으로 중복 저장이 방지됩니다."""
    log = EventLog(
        event_id=request.event_id,
        session_id=request.session_id,
        user_id=request.user_id,
        anon_id=request.anon_id,
        event_name=request.event_name,
        occurred_at=datetime.now(),
        extra_data=request.extra_data,
    )
    db.add(log)
    db.commit()
    logger.debug("이벤트 저장. event_name=%s, session_id=%s", request.event_name, request.session_id)
