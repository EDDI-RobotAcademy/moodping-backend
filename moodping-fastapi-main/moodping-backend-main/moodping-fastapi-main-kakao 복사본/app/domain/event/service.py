import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.domain.event.models import EventLog
from app.domain.event.schemas import EventLogRequest

logger = logging.getLogger(__name__)

DROP_THRESHOLD_MINUTES = 10
RETENTION_DAYS = 7


def save(request: EventLogRequest, db: Session) -> None:
    log = EventLog(
        event_id=request.event_id,
        session_id=request.session_id,
        user_id=request.user_id,
        anon_id=request.anon_id,
        event_name=request.event_name,
        occurred_at=datetime.now(),
        extra_data=request.extra_data,
    )
    db.add(log)
    db.commit()
    logger.debug("이벤트 저장. event_name=%s, session_id=%s", request.event_name, request.session_id)


def get_recent_records(db: Session) -> list[dict]:
    sql = text("""
        SELECT
            mr.id          AS record_id,
            mr.anon_id     AS anon_id,
            mr.user_id     AS user_id,
            mr.mood_emoji  AS emoji,
            mr.intensity   AS intensity,
            mr.mood_text   AS mood_text,
            ma.analysis_text AS analysis_text,
            mr.recorded_at AS recorded_at
        FROM mood_record mr
        LEFT JOIN mood_analysis ma ON ma.record_id = mr.id
        ORDER BY mr.recorded_at DESC
        LIMIT 10
    """)
    rows = db.execute(sql).mappings().all()
    return [
        {
            "record_id":     row["record_id"],
            "anon_id":       row["anon_id"],
            "user_id":       row["user_id"],
            "emoji":         row["emoji"],
            "intensity":     row["intensity"],
            "mood_text":     row["mood_text"],
            "analysis_text": row["analysis_text"],
            "recorded_at":   str(row["recorded_at"]) if row["recorded_at"] else None,
        }
        for row in rows
    ]


def get_metrics(db: Session) -> dict:
    return {
        "drop_threshold_minutes": DROP_THRESHOLD_MINUTES,
        "funnel": {
            "record_funnel":   _record_funnel(db),
            "analysis_funnel": _analysis_funnel(db),
        },
        "step_funnel": _step_funnel(db),
        "retention": _retention(db),
    }


def _record_funnel(db: Session) -> dict:
    sql = text("""
        SELECT
            COUNT(DISTINCT s.session_id)                           AS record_start_count,
            COUNT(DISTINCT c.session_id)                           AS record_complete_count,
            ROUND(
                CASE WHEN COUNT(DISTINCT s.session_id) = 0 THEN 0
                     ELSE 1.0 - COUNT(DISTINCT c.session_id) * 1.0
                              / COUNT(DISTINCT s.session_id)
                END, 4
            )                                                      AS record_drop_rate,
            ROUND(
                COALESCE(
                    AVG(CASE WHEN c.session_id IS NOT NULL
                             THEN TIMESTAMPDIFF(SECOND, s.occurred_at, c.occurred_at)
                        END) / 60.0,
                0), 2
            )                                                      AS avg_record_duration_minutes
        FROM event_log s
        LEFT JOIN event_log c
            ON  s.session_id  = c.session_id
            AND c.event_name  = 'record_complete'
            AND TIMESTAMPDIFF(MINUTE, s.occurred_at, c.occurred_at) BETWEEN 0 AND :threshold
        WHERE s.event_name = 'record_screen_view'
    """)
    row = db.execute(sql, {"threshold": DROP_THRESHOLD_MINUTES}).mappings().first()
    return _safe_funnel_row(row, "record_start_count", "record_complete_count",
                            "record_drop_rate", "avg_record_duration_minutes")


def _analysis_funnel(db: Session) -> dict:
    sql = text("""
        SELECT
            COUNT(DISTINCT rc.session_id)                          AS record_complete_count,
            COUNT(DISTINCT av.session_id)                          AS analysis_view_count,
            ROUND(
                CASE WHEN COUNT(DISTINCT rc.session_id) = 0 THEN 0
                     ELSE 1.0 - COUNT(DISTINCT av.session_id) * 1.0
                              / COUNT(DISTINCT rc.session_id)
                END, 4
            )                                                      AS analysis_drop_rate,
            ROUND(
                COALESCE(
                    AVG(CASE WHEN av.session_id IS NOT NULL
                             THEN TIMESTAMPDIFF(SECOND, rc.occurred_at, av.occurred_at)
                        END) / 60.0,
                0), 2
            )                                                      AS avg_analysis_duration_minutes
        FROM event_log rc
        LEFT JOIN event_log av
            ON  rc.session_id = av.session_id
            AND av.event_name = 'analysis_view'
            AND TIMESTAMPDIFF(MINUTE, rc.occurred_at, av.occurred_at) BETWEEN 0 AND :threshold
        WHERE rc.event_name = 'record_complete'
    """)
    row = db.execute(sql, {"threshold": DROP_THRESHOLD_MINUTES}).mappings().first()
    return _safe_funnel_row(row, "record_complete_count", "analysis_view_count",
                            "analysis_drop_rate", "avg_analysis_duration_minutes")


def _retention(db: Session) -> dict:
    sql = text("""
        SELECT
            COUNT(DISTINCT fv.identifier)                          AS total_users,
            COUNT(DISTINCT rv.identifier)                          AS retained_users,
            ROUND(
                CASE WHEN COUNT(DISTINCT fv.identifier) = 0 THEN 0
                     ELSE COUNT(DISTINCT rv.identifier) * 100.0
                          / COUNT(DISTINCT fv.identifier)
                END, 2
            )                                                      AS retention_rate_percent
        FROM (
            SELECT
                COALESCE(user_id, anon_id) AS identifier,
                MIN(occurred_at)           AS first_view_at
            FROM event_log
            WHERE event_name = 'analysis_view'
              AND COALESCE(user_id, anon_id) IS NOT NULL
            GROUP BY COALESCE(user_id, anon_id)
        ) fv
        LEFT JOIN (
            SELECT
                COALESCE(user_id, anon_id) AS identifier,
                occurred_at
            FROM event_log
            WHERE event_name = 'analysis_view'
              AND COALESCE(user_id, anon_id) IS NOT NULL
        ) rv
            ON  fv.identifier = rv.identifier
            AND rv.occurred_at > fv.first_view_at
            AND DATEDIFF(rv.occurred_at, fv.first_view_at) <= :days
    """)
    row = db.execute(sql, {"days": RETENTION_DAYS}).mappings().first()
    if not row:
        return {"total_users": 0, "retained_users": 0, "retention_rate_percent": 0.0,
                "retention_window_days": RETENTION_DAYS}
    return {
        "total_users":            int(row["total_users"] or 0),
        "retained_users":         int(row["retained_users"] or 0),
        "retention_rate_percent": float(row["retention_rate_percent"] or 0.0),
        "retention_window_days":  RETENTION_DAYS,
    }


FUNNEL_STEPS = [
    "record_screen_view",
    "emoji_selected",
    "intensity_selected",
    "text_input_start",
    "record_complete",
    "analysis_view",
    "feedback_confirmed",
]

STEP_LABELS = {
    "record_screen_view": "페이지 진입",
    "emoji_selected":     "이모지 선택",
    "intensity_selected": "강도 선택",
    "text_input_start":   "텍스트 입력",
    "record_complete":    "기록 완료",
    "analysis_view":      "분석 조회",
    "feedback_confirmed": "확인 완료",
}


def _step_funnel(db: Session) -> list[dict]:
    placeholders = ", ".join(f":s{i}" for i in range(len(FUNNEL_STEPS)))
    sql = text(f"""
        SELECT event_name, COUNT(DISTINCT session_id) AS sessions
        FROM event_log
        WHERE event_name IN ({placeholders})
        GROUP BY event_name
    """)
    params = {f"s{i}": step for i, step in enumerate(FUNNEL_STEPS)}
    rows = db.execute(sql, params).mappings().all()
    counts = {row["event_name"]: int(row["sessions"]) for row in rows}

    result = []
    for i, step in enumerate(FUNNEL_STEPS):
        current = counts.get(step, 0)
        prev = counts.get(FUNNEL_STEPS[i - 1], 0) if i > 0 else current
        drop_rate = round(1.0 - current / prev, 4) if prev > 0 else 0.0
        result.append({
            "step": step,
            "label": STEP_LABELS[step],
            "sessions": current,
            "drop_rate": drop_rate,
        })
    return result


def _safe_funnel_row(row, k0: str, k1: str, k2: str, k3: str) -> dict:
    if not row:
        return {k0: 0, k1: 0, k2: 0.0, k3: 0.0}
    return {
        k0: int(row[k0] or 0),
        k1: int(row[k1] or 0),
        k2: float(row[k2] or 0.0),
        k3: float(row[k3] or 0.0),
    }
