from sqlalchemy import BigInteger, Column, String, Text, DateTime, Date, Integer, Numeric, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class WeeklyReport(Base):
    __tablename__ = "weekly_report"

    id                = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id           = Column(BigInteger, nullable=False, index=True)
    week_start        = Column(Date, nullable=False)
    week_end          = Column(Date, nullable=False)
    summary_text      = Column(Text, nullable=True)
    record_count      = Column(Integer, nullable=False, default=0)
    avg_intensity     = Column(Numeric(3, 1), nullable=True)
    mood_distribution = Column(JSON, nullable=True)
    created_at        = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "week_start", name="uk_user_week"),
    )
