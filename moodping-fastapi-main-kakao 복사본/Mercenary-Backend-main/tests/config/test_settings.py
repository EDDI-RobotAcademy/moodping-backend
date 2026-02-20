# tests/test_settings.py

import pytest
from config.settings import Settings


def test_settings_load(monkeypatch):
    monkeypatch.setenv("KAKAO_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("KAKAO_REDIRECT_URI", "http://localhost/test")

    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_PASSWORD", "")
    monkeypatch.setenv("REDIS_DB", "1")

    monkeypatch.setenv("MYSQL_USER", "test_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "test_pass")
    monkeypatch.setenv("MYSQL_HOST", "localhost")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_DB", "mercenary_db")

    settings = Settings()

    assert settings.KAKAO_CLIENT_ID == "test-client-id"
    assert settings.REDIS_HOST == "localhost"
    assert settings.REDIS_PORT == 6379
    assert settings.REDIS_DB == 1
    assert settings.MYSQL_DB == "mercenary_db"
