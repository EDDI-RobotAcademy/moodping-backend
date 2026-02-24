from datetime import datetime, date
from sqlalchemy import BigInteger, Column, String, DateTime, Date, SmallInteger
from sqlalchemy.sql import func
from moodping.config.mysql_config import Base

class MoodRecord(Base):
    __tablename__ = "mood_record"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=True, index=True)
    anon_id = Column(String(100), nullable=True, index=True)
    record_date = Column(Date, nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    mood_emoji = Column(String(20), nullable=False)
    intensity = Column(SmallInteger, nullable=False)
    mood_text = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    @classmethod
    def create(
        cls,
        mood_emoji: str,
        intensity: int,
        mood_text: str | None,
        user_id: str | None = None,
        anon_id: str | None = None,
        record_date: date | None = None,
        recorded_at: datetime | None = None,
    ) -> "MoodRecord":
        if not mood_emoji or not mood_emoji.strip():
            raise ValueError("mood_emoji must not be empty")
        if not (0 <= intensity <= 10):
            raise ValueError("intensity must be between 0 and 10")
        if mood_text is not None and len(mood_text) > 500:
            raise ValueError("mood_text must not exceed 500 characters")

        now = recorded_at or datetime.now()
        rdate = record_date or now.date()

        return cls(
            mood_emoji=mood_emoji.strip(),
            intensity=intensity,
            mood_text=(mood_text or "").strip() or None,
            user_id=user_id,
            anon_id=anon_id,
            record_date=rdate,
            recorded_at=now,
        )
