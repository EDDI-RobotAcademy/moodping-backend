from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional, Type, TypeVar

T = TypeVar("T")


class RedisCacheRepository(ABC):

    @abstractmethod
    def set_key_and_value(self, key, value, ttl: Optional[timedelta] = None):
        pass

    @abstractmethod
    def get_value_by_key(self, key: str, clazz: Type[T]) -> Optional[T]:
        pass

    @abstractmethod
    def delete_by_key(self, key: str):
        pass

    @abstractmethod
    def is_refresh_token_exists(self, token: str) -> bool:
        pass
