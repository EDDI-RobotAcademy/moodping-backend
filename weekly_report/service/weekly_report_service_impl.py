import json
import logging
import re
from collections import Counter
from datetime import date, timedelta
from sqlalchemy.orm import Session

from moodping.config.mysql_config import SessionLocal
from moodping.weekly_report.domain.entity.weekly_report import WeeklyReport
from moodping.weekly_report.repository.weekly_report_repository_impl import WeeklyReportRepositoryImpl
from moodping.weekly_report.service.weekly_report_service import WeeklyReportService
# prompt build를 위해 app 경로 참조
from moodping.weekly_report.prompt.report_prompt import SYSTEM_PROMPT, build
from moodping.mood_record.repository.mood_record_repository_impl import MoodRecordRepositoryImpl
from moodping.llm.factory import get_llm_client

logger = logging.getLogger(__name__)

class WeeklyReportServiceImpl(WeeklyReportService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls) -> "WeeklyReportServiceImpl":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        self.weekly_report_repository = WeeklyReportRepositoryImpl.get_instance()
        self.mood_record_repository = MoodRecordRepositoryImpl.get_instance()

    async def get_or_create_latest_report(self, user_id: int) -> dict:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        session: Session = SessionLocal()
        try:
            existing = self.weekly_report_repository.find_by_user_and_week(session, user_id, week_start)
            if existing:
                return self._to_dict(existing)

            records = self.mood_record_repository.find_7days_by_user(session, str(user_id))
            if not records:
                return {
                    "week_start": week_start.isoformat(),
                    "week_end": week_end.isoformat(),
                    "record_count": 0,
                    "avg_intensity": None,
                    "mood_distribution": [],
                    "summary_text": "이번 주 감정 기록이 없습니다. 감정을 기록해보세요!",
                }

            record_count = len(records)
            avg_intensity = round(sum(r.intensity for r in records) / record_count, 1)
            mood_distribution = self._build_distribution(records)

            record_dicts = [
                {
                    "record_date": str(r.record_date),
                    "mood_emoji": r.mood_emoji,
                    "intensity": r.intensity,
                    "mood_text": r.mood_text or "",
                }
                for r in records
            ]
            mood_counts = {d["emoji"]: d["count"] for d in mood_distribution}
            summary_text = await self._generate_summary(record_dicts, avg_intensity, mood_counts)
            if not summary_text:
                summary_text = f"이번 주 {record_count}건의 감정을 기록하셨네요. 평균 강도는 {avg_intensity}/10입니다."

            report = WeeklyReport.create(
                user_id=user_id,
                week_start=week_start,
                week_end=week_end,
                summary_text=summary_text,
                record_count=record_count,
                avg_intensity=avg_intensity,
                mood_distribution=mood_distribution,
            )
            self.weekly_report_repository.save(session, report)
            session.commit()
            session.refresh(report)
            return self._to_dict(report)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _build_distribution(self, records) -> list[dict]:
        counts = Counter(r.mood_emoji for r in records)
        return [{"emoji": emoji, "count": count} for emoji, count in counts.most_common()]

    async def _generate_summary(self, records: list[dict], avg_intensity: float, mood_counts: dict[str, int]) -> str | None:
        try:
            llm = get_llm_client()
            user_prompt = build(records, avg_intensity, mood_counts)
            raw = await llm.complete(SYSTEM_PROMPT, user_prompt)
            return self._parse_summary(raw) if raw else None
        except Exception as e:
            logger.error("주간 리포트 LLM 요약 실패: %s", e)
            return None

    def _parse_summary(self, content: str) -> str | None:
        if not content:
            return None
        match = re.search(r'"summary_text"\s*:\s*"((?:[^"\\]|\\.)*)"', content, re.DOTALL)
        if not match:
            match = re.search(r'"summary_text"\s*:\s*"((?:[^"\\]|\\.)*)', content, re.DOTALL)
        if match:
            raw = match.group(1)
            text = raw.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
            return text[:3000] if text.strip() else None
        try:
            cleaned = re.sub(r"```(?:json)?\s*", "", content, flags=re.IGNORECASE)
            cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE).strip()
            data = json.loads(cleaned)
            text = data.get("summary_text", "")
            return text[:3000] if text.strip() else None
        except (json.JSONDecodeError, AttributeError):
            return content[:3000]

    def _to_dict(self, report: WeeklyReport) -> dict:
        return {
            "id": report.id,
            "week_start": report.week_start.isoformat() if report.week_start else None,
            "week_end": report.week_end.isoformat() if report.week_end else None,
            "record_count": report.record_count,
            "avg_intensity": float(report.avg_intensity) if report.avg_intensity is not None else None,
            "mood_distribution": report.mood_distribution or [],
            "summary_text": report.summary_text,
        }
