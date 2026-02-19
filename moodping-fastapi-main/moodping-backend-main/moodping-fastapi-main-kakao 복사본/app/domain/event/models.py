from sqlalchemy import BigInteger, Column, String, DateTime, JSON
from app.database import Base


class EventLog(Base):
    __tablename__ = "event_log"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id    = Column(String(100), nullable=False, unique=True)
    session_id  = Column(String(100), nullable=False, index=True)
    user_id     = Column(String(100), nullable=True, index=True)
    anon_id     = Column(String(100), nullable=True, index=True)
    event_name  = Column(String(50), nullable=False, index=True)
    occurred_at = Column(DateTime, nullable=False, index=True)
    extra_data  = Column(JSON, nullable=True)
