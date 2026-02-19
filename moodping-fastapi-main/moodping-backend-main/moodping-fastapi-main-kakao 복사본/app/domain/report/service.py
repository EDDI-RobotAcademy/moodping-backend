import json
import logging
import re
from collections import Counter
from sqlalchemy.orm import Session

from app.domain.report.models import WeeklyReport
from app.domain.report.schemas import WeeklyReportResponse, MoodDistributionItem
from app.domain.report.dummy_data import (
    get_dummy_records, get_dummy_week_range, EMOJI_MAP, LABEL_KO,
)
from app.llm.factory import get_llm_client
from app.prompt import report_prompt

logger = logging.getLogger(__name__)


async def get_or_create_latest_report(user_id: int | None, db: Session) -> WeeklyReportResponse:
    week_start, week_end = get_dummy_week_range()

    if user_id:
        existing = (
            db.query(WeeklyReport)
            .filter(WeeklyReport.user_id == user_id, WeeklyReport.week_start == week_start)
            .first()
        )
        if existing:
            return _to_response(existing)

    records = get_dummy_records()
    distribution = _build_distribution(records)
    avg_intensity = sum(r["intensity"] for r in records) / len(records)

    summary_text = await _generate_summary(records, avg_intensity, distribution)
    if not summary_text:
        summary_text = (
            f"이번 주 {len(records)}건의 감정을 기록하셨네요. "
            f"평균 강도는 {avg_intensity:.1f}/10입니다. "
            "일주일간 마음을 돌아보신 것만으로도 의미 있는 일이에요. "
            "다음 주에도 꾸준히 기록해보세요."
        )

    if user_id:
        report = WeeklyReport(
            user_id=user_id,
            week_start=week_start,
            week_end=week_end,
            summary_text=summary_text,
            record_count=len(records),
            avg_intensity=round(avg_intensity, 1),
            mood_distribution=[
                {"emoji": d.emoji, "label_ko": d.label_ko, "count": d.count}
                for d in distribution
            ],
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return _to_response(report)

    return WeeklyReportResponse(
        week_start=week_start,
        week_end=week_end,
        record_count=len(records),
        avg_intensity=round(avg_intensity, 1),
        mood_distribution=distribution,
        summary_text=summary_text,
        is_dummy=True,
    )


def _build_distribution(records: list[dict]) -> list[MoodDistributionItem]:
    counts = Counter(r["mood_emoji"] for r in records)
    result = []
    for label, count in counts.most_common():
        result.append(MoodDistributionItem(
            emoji=EMOJI_MAP.get(label, ""),
            label_ko=LABEL_KO.get(label, label),
            count=count,
        ))
    return result


async def _generate_summary(records: list[dict], avg_intensity: float, distribution: list) -> str | None:
    try:
        mood_counts = {}
        for d in distribution:
            mood_counts[f"{d.emoji} {d.label_ko}"] = d.count

        record_dicts = []
        for r in records:
            emoji = EMOJI_MAP.get(r["mood_emoji"], "")
            label = LABEL_KO.get(r["mood_emoji"], r["mood_emoji"])
            record_dicts.append({
                "record_date": str(r["record_date"]),
                "mood_emoji": f"{emoji} {label}",
                "intensity": r["intensity"],
                "mood_text": r.get("mood_text", ""),
            })

        llm = get_llm_client()
        system_prompt = report_prompt.SYSTEM_PROMPT
        user_prompt = report_prompt.build(record_dicts, avg_intensity, mood_counts)
        raw = await llm.complete(system_prompt, user_prompt)

        if not raw:
            return None

        return _parse_summary_text(raw)

    except Exception as e:
        logger.error("주간 리포트 LLM 요약 실패: %s", e)
        return None


def _parse_summary_text(content: str) -> str | None:
    if not content:
        return None

    match = re.search(
        r'"summary_text"\s*:\s*"((?:[^"\\]|\\.)*)"',
        content,
        re.DOTALL,
    )
    if not match:
        match = re.search(
            r'"summary_text"\s*:\s*"((?:[^"\\]|\\.)*)',
            content,
            re.DOTALL,
        )
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
        logger.warning("summary_text 파싱 실패 — raw 반환")
        return content[:3000]


def _to_response(report: WeeklyReport) -> WeeklyReportResponse:
    dist_raw = report.mood_distribution or []
    distribution = [
        MoodDistributionItem(
            emoji=d.get("emoji", ""),
            label_ko=d.get("label_ko", ""),
            count=d.get("count", 0),
        )
        for d in dist_raw
    ]
    return WeeklyReportResponse(
        id=report.id,
        week_start=report.week_start,
        week_end=report.week_end,
        record_count=report.record_count,
        avg_intensity=float(report.avg_intensity) if report.avg_intensity else None,
        mood_distribution=distribution,
        summary_text=report.summary_text,
        is_dummy=False,
    )
