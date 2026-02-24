from abc import ABC, abstractmethod
from datetime import date
from moodping.mood_record.domain.entity.mood_record import MoodRecord

class MoodRecordService(ABC):
    @abstractmethod
    def create(self, mood_emoji: str, intensity: int, mood_text: str | None, user_id: str | None = None, anon_id: str | None = None) -> MoodRecord:
        pass

    @abstractmethod
    def find_by_id(self, record_id: int) -> MoodRecord | None:
        pass

    @abstractmethod
    def find_by_user(self, user_id: str, limit: int | None = None) -> list[MoodRecord]:
        pass

    @abstractmethod
    def find_7days_by_user(self, user_id: str, end_date: date | None = None) -> list[MoodRecord]:
        pass

    @abstractmethod
    def link_anon_to_user(self, user_id: str, anon_id: str) -> int:
        pass
