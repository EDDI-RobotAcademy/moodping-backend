from sqlalchemy import BigInteger, Column, String, Text, DateTime, Date, SmallInteger, JSON, UniqueConstraint, Index
from sqlalchemy.sql import func
from .database import Base


class MoodRecord(Base):
    __tablename__ = "mood_record"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id     = Column(String(100), nullable=True, index=True)
    anon_id     = Column(String(100), nullable=True, index=True)
    record_date = Column(Date, nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    mood_emoji  = Column(String(20), nullable=False)
    intensity   = Column(SmallInteger, nullable=False)
    mood_text   = Column(String(500), nullable=True)
    created_at  = Column(DateTime, nullable=False, server_default=func.now())
    updated_at  = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class MoodAnalysis(Base):
    __tablename__ = "mood_analysis"

    id            = Column(BigInteger, primary_key=True, autoincrement=True)
    record_id     = Column(BigInteger, nullable=False, index=True)
    user_id       = Column(String(100), nullable=True)
    analysis_text = Column(Text, nullable=True)
    created_at    = Column(DateTime, nullable=False, server_default=func.now())


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
