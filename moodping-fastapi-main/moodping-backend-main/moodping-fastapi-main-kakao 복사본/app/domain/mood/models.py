from sqlalchemy import BigInteger, Column, String, Text, DateTime, Date, SmallInteger
from sqlalchemy.sql import func
from app.database import Base


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
