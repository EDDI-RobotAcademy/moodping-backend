from abc import ABC, abstractmethod
from datetime import date
from sqlalchemy.orm import Session
from moodping.mood_record.domain.entity.mood_record import MoodRecord

class MoodRecordRepository(ABC):
    @abstractmethod
    def save(self, session: Session, record: MoodRecord) -> MoodRecord:
        pass

    @abstractmethod
    def find_by_id(self, session: Session, record_id: int) -> MoodRecord | None:
        pass

    @abstractmethod
    def find_by_user(self, session: Session, user_id: str, limit: int | None = None) -> list[MoodRecord]:
        pass

    @abstractmethod
    def find_7days_by_user(self, session: Session, user_id: str, end_date: date | None = None) -> list[MoodRecord]:
        pass

    @abstractmethod
    def link_anon_to_user(self, session: Session, user_id: str, anon_id: str) -> int:
        pass
