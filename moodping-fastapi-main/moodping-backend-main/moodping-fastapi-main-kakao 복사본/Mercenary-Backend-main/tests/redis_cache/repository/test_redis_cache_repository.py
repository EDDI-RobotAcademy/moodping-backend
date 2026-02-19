import pytest
import time
from datetime import timedelta
from unittest.mock import MagicMock, patch

from redis_cache.repository.redis_cache_repository_impl import RedisCacheRepositoryImpl
from config.settings import Settings

@pytest.fixture(scope="module")
def redis_service():
    # Redis 관련 설정만
    mock_settings_obj = Settings(
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_PASSWORD="dummy_password",
        REDIS_DB=0
    )

    with patch("config.settings.get_settings", return_value=mock_settings_obj):
        instance = RedisCacheRepositoryImpl.__new__(RedisCacheRepositoryImpl)

        # Redis client를 MagicMock으로 교체
        instance.redis_client = MagicMock()
        yield instance


def test_set_and_get(redis_service):
    redis_service.set_key_and_value("test:key", "value1")
    redis_service.redis_client.get.return_value = "value1"
    result = redis_service.get_value_by_key("test:key", str)
    assert result == "value1"


def test_delete(redis_service):
    redis_service.set_key_and_value("delete:key", "value2")
    redis_service.delete_by_key("delete:key")
    redis_service.redis_client.get.return_value = None
    result = redis_service.get_value_by_key("delete:key", str)
    assert result is None


def test_ttl_expiration(redis_service):
    redis_service.set_key_and_value("ttl:key", "temp", ttl=timedelta(seconds=2))
    redis_service.redis_client.get.return_value = None
    time.sleep(3)
    result = redis_service.get_value_by_key("ttl:key", str)
    assert result is None


def test_refresh_token_exists(redis_service):
    token = "refresh:token:123"
    redis_service.set_key_and_value(token, "user1")
    redis_service.redis_client.exists.return_value = 1
    assert redis_service.is_refresh_token_exists(token) is True

    redis_service.delete_by_key(token)
    redis_service.redis_client.exists.return_value = 0
    assert redis_service.is_refresh_token_exists(token) is False
