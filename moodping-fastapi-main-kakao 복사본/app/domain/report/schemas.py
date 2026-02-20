from pydantic import BaseModel
import datetime


class MoodDistributionItem(BaseModel):
    emoji: str
    label_ko: str
    count: int


class WeeklyReportResponse(BaseModel):
    id: int | None = None
    week_start: datetime.date
    week_end: datetime.date
    record_count: int
    avg_intensity: float | None
    mood_distribution: list[MoodDistributionItem]
    summary_text: str | None
    is_dummy: bool = False
