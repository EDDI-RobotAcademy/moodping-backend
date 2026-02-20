from sqlalchemy.orm import Session
from sqlalchemy import text

from event_log.domain.entity.event_log import EventLog
from event_log.repository.event_log_repository import EventLogRepository


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
    "emoji_selected": "이모지 선택",
    "intensity_selected": "강도 선택",
    "text_input_start": "텍스트 입력",
    "record_complete": "기록 완료",
    "analysis_view": "분석 조회",
    "feedback_confirmed": "확인 완료",
}


class EventLogRepositoryImpl(EventLogRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def save(self, session: Session, event_log: EventLog) -> EventLog:
        session.add(event_log)
        session.flush()
        return event_log

    def get_record_funnel(self, session: Session, threshold_minutes: int) -> dict:
        sql = text("""
            SELECT
                COUNT(DISTINCT s.session_id)                           AS record_start_count,
                COUNT(DISTINCT c.session_id)                           AS record_complete_count,
                ROUND(
                    CASE WHEN COUNT(DISTINCT s.session_id) = 0 THEN 0
                         ELSE 1.0 - COUNT(DISTINCT c.session_id) * 1.0
                                  / COUNT(DISTINCT s.session_id)
                    END, 4
                )                                                    AS record_drop_rate,
                ROUND(
                    COALESCE(
                        AVG(CASE WHEN c.session_id IS NOT NULL
                                 THEN TIMESTAMPDIFF(SECOND, s.occurred_at, c.occurred_at)
                            END) / 60.0,
                    0), 2
                )                                                    AS avg_record_duration_minutes
            FROM event_log s
            LEFT JOIN event_log c
                ON  s.session_id  = c.session_id
                AND c.event_name  = 'record_complete'
                AND TIMESTAMPDIFF(MINUTE, s.occurred_at, c.occurred_at) BETWEEN 0 AND :threshold
            WHERE s.event_name = 'record_screen_view'
        """)
        row = session.execute(sql, {"threshold": threshold_minutes}).mappings().first()
        return self._safe_funnel_row(
            row, "record_start_count", "record_complete_count",
            "record_drop_rate", "avg_record_duration_minutes"
        )

    def get_analysis_funnel(self, session: Session, threshold_minutes: int) -> dict:
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
        row = session.execute(sql, {"threshold": threshold_minutes}).mappings().first()
        return self._safe_funnel_row(
            row, "record_complete_count", "analysis_view_count",
            "analysis_drop_rate", "avg_analysis_duration_minutes"
        )

    def get_step_funnel(self, session: Session, step_names: list[str]) -> list[dict]:
        placeholders = ", ".join(f":s{i}" for i in range(len(step_names)))
        sql = text(f"""
            SELECT event_name, COUNT(DISTINCT session_id) AS sessions
            FROM event_log
            WHERE event_name IN ({placeholders})
            GROUP BY event_name
        """)
        params = {f"s{i}": step for i, step in enumerate(step_names)}
        rows = session.execute(sql, params).mappings().all()
        counts = {row["event_name"]: int(row["sessions"]) for row in rows}

        result = []
        for i, step in enumerate(step_names):
            current = counts.get(step, 0)
            prev = counts.get(step_names[i - 1], 0) if i > 0 else current
            drop_rate = round(1.0 - current / prev, 4) if prev > 0 else 0.0
            result.append({
                "step": step,
                "label": STEP_LABELS.get(step, step),
                "sessions": current,
                "drop_rate": drop_rate,
            })
        return result

    def get_retention(self, session: Session, retention_days: int) -> dict:
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
        row = session.execute(sql, {"days": retention_days}).mappings().first()
        if not row:
            return {
                "total_users": 0,
                "retained_users": 0,
                "retention_rate_percent": 0.0,
                "retention_window_days": retention_days,
            }
        return {
            "total_users": int(row["total_users"] or 0),
            "retained_users": int(row["retained_users"] or 0),
            "retention_rate_percent": float(row["retention_rate_percent"] or 0.0),
            "retention_window_days": retention_days,
        }

    def _safe_funnel_row(
        self, row, k0: str, k1: str, k2: str, k3: str
    ) -> dict:
        if not row:
            return {k0: 0, k1: 0, k2: 0.0, k3: 0.0}
        return {
            k0: int(row[k0] or 0),
            k1: int(row[k1] or 0),
            k2: float(row[k2] or 0.0),
            k3: float(row[k3] or 0.0),
        }
