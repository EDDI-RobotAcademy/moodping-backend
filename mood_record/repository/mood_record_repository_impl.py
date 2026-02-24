from datetime import date, timedelta
from sqlalchemy.orm import Session
from moodping.mood_record.domain.entity.mood_record import MoodRecord
from moodping.mood_record.repository.mood_record_repository import MoodRecordRepository

class MoodRecordRepositoryImpl(MoodRecordRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls) -> "MoodRecordRepositoryImpl":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def save(self, session: Session, record: MoodRecord) -> MoodRecord:
        session.add(record)
        session.flush()
        return record

    def find_by_id(self, session: Session, record_id: int) -> MoodRecord | None:
        return session.get(MoodRecord, record_id)

    def find_by_user(self, session: Session, user_id: str, limit: int | None = None) -> list[MoodRecord]:
        q = session.query(MoodRecord).filter(MoodRecord.user_id == user_id).order_by(MoodRecord.recorded_at.desc())
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    def find_7days_by_user(self, session: Session, user_id: str, end_date: date | None = None) -> list[MoodRecord]:
        end = end_date or date.today()
        start = end - timedelta(days=6)
        return session.query(MoodRecord).filter(
            MoodRecord.user_id == user_id,
            MoodRecord.record_date >= start,
            MoodRecord.record_date <= end,
        ).order_by(MoodRecord.record_date.asc(), MoodRecord.recorded_at.asc()).all()

    def link_anon_to_user(self, session: Session, user_id: str, anon_id: str) -> int:
        updated = session.query(MoodRecord).filter(
            MoodRecord.anon_id == anon_id,
            MoodRecord.user_id.is_(None),
        ).update({"user_id": user_id, "anon_id": None}, synchronize_session=False)
        return updated
