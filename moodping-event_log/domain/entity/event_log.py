from datetime import datetime

from sqlalchemy import BigInteger, Column, String, DateTime, JSON

from app.database import Base


class EventLog(Base):
    """이벤트 추적 엔티티"""

    __tablename__ = "event_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(String(100), nullable=False, unique=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    anon_id = Column(String(100), nullable=True, index=True)
    event_name = Column(String(50), nullable=False, index=True)
    occurred_at = Column(DateTime, nullable=False, index=True)
    extra_data = Column(JSON, nullable=True)

    @classmethod
    def create(
        cls,
        event_id: str,
        session_id: str,
        event_name: str,
        user_id: str | None = None,
        anon_id: str | None = None,
        extra_data: dict | None = None,
        occurred_at: datetime | None = None,
    ) -> "EventLog":
        if not event_id or not event_id.strip():
            raise ValueError("event_id must not be empty")
        if not session_id or not session_id.strip():
            raise ValueError("session_id must not be empty")
        if not event_name or not event_name.strip():
            raise ValueError("event_name must not be empty")
        if len(event_name) > 50:
            raise ValueError("event_name must not exceed 50 characters")

        return cls(
            event_id=event_id.strip(),
            session_id=session_id.strip(),
            event_name=event_name.strip(),
            user_id=user_id,
            anon_id=anon_id,
            extra_data=extra_data,
            occurred_at=occurred_at or datetime.utcnow(),
        )
