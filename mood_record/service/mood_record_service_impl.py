from datetime import date
from moodping.mood_record.domain.entity.mood_record import MoodRecord
from moodping.mood_record.repository.mood_record_repository_impl import MoodRecordRepositoryImpl
from moodping.mood_record.service.mood_record_service import MoodRecordService
from moodping.config.mysql_config import SessionLocal

class MoodRecordServiceImpl(MoodRecordService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls) -> "MoodRecordServiceImpl":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        self._repository = MoodRecordRepositoryImpl.get_instance()

    def create(self, mood_emoji: str, intensity: int, mood_text: str | None, user_id: str | None = None, anon_id: str | None = None) -> MoodRecord:
        record = MoodRecord.create(
            mood_emoji=mood_emoji,
            intensity=intensity,
            mood_text=mood_text,
            user_id=user_id,
            anon_id=anon_id,
        )
        session = SessionLocal()
        try:
            self._repository.save(session, record)
            session.commit()
            session.refresh(record)
            return record
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def find_by_id(self, record_id: int) -> MoodRecord | None:
        session = SessionLocal()
        try:
            return self._repository.find_by_id(session, record_id)
        finally:
            session.close()

    def find_by_user(self, user_id: str, limit: int | None = None) -> list[MoodRecord]:
        session = SessionLocal()
        try:
            return self._repository.find_by_user(session, user_id, limit=limit)
        finally:
            session.close()

    def find_7days_by_user(self, user_id: str, end_date: date | None = None) -> list[MoodRecord]:
        session = SessionLocal()
        try:
            return self._repository.find_7days_by_user(session, user_id, end_date=end_date)
        finally:
            session.close()

    def link_anon_to_user(self, user_id: str, anon_id: str) -> int:
        session = SessionLocal()
        try:
            updated = self._repository.link_anon_to_user(session, user_id, anon_id)
            session.commit()
            return updated
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
