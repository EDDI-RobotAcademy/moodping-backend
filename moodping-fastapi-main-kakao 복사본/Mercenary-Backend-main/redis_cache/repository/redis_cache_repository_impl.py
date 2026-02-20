from datetime import timedelta
from typing import Optional, Type, TypeVar

from config.redis_config import RedisConfig
from redis_cache.repository.redis_cache_repository import RedisCacheRepository

T = TypeVar("T")


class RedisCacheRepositoryImpl(RedisCacheRepository):
    _instance = None
    DEFAULT_TTL = timedelta(minutes=720)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.redis_client = RedisConfig().get_client()
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_key_and_value(self, key, value, ttl: Optional[timedelta] = None):
        key_str = str(key)
        value_str = str(value)

        if ttl is None:
            ttl = self.DEFAULT_TTL

        ttl_seconds = int(ttl.total_seconds())

        self.redis_client.set(name=key_str, value=value_str, ex=ttl_seconds)

    def get_value_by_key(self, key: str, clazz: Type[T]) -> Optional[T]:
        value = self.redis_client.get(key)

        if value is None:
            return None

        if clazz == str:
            return value
        if clazz == int:
            return int(value)
        if clazz == float:
            return float(value)

        raise ValueError(f"지원하지 않는 타입: {clazz}")

    def delete_by_key(self, key: str):
        self.redis_client.delete(key)

    def is_refresh_token_exists(self, token: str) -> bool:
        return self.redis_client.exists(token) == 1
