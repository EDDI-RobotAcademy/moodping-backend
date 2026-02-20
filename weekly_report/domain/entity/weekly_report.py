from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, Column, Integer, Text, Date, DateTime,
    Numeric, JSON, UniqueConstraint,
)
from sqlalchemy.sql import func

from config.mysql_config import MySQLConfig

Base = MySQLConfig().get_base()


class WeeklyReport(Base):
    __tablename__ = "weekly_report"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    summary_text = Column(Text, nullable=True)
    record_count = Column(Integer, nullable=False, default=0)
    avg_intensity = Column(Numeric(3, 1), nullable=True)
    mood_distribution = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "week_start", name="uk_user_week"),
    )

    @classmethod
    def create(
        cls,
        user_id: int,
        week_start: date,
        week_end: date,
        summary_text: str | None,
        record_count: int,
        avg_intensity: float | None,
        mood_distribution: list | None,
    ) -> "WeeklyReport":
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")

        if week_end < week_start:
            raise ValueError("week_end must be after week_start")

        if record_count < 0:
            raise ValueError("record_count must be non-negative")

        if avg_intensity is not None and not (0 <= avg_intensity <= 10):
            raise ValueError("avg_intensity must be between 0 and 10")

        return cls(
            user_id=user_id,
            week_start=week_start,
            week_end=week_end,
            summary_text=summary_text,
            record_count=record_count,
            avg_intensity=round(avg_intensity, 1) if avg_intensity is not None else None,
            mood_distribution=mood_distribution or [],
        )
