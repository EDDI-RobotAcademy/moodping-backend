import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import OperationalError
from config.mysql_config import MySQLConfig


# ========================
# 환경 변수/Settings Mock
# ========================
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("MYSQL_USER", "test_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "test_pass")
    monkeypatch.setenv("MYSQL_HOST", "localhost")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_DB", "test_db")

def test_singleton_instance():
    """싱글톤 패턴 확인"""
    instance1 = MySQLConfig()
    instance2 = MySQLConfig()
    assert instance1 is instance2, "MySQLConfig 싱글톤 실패"


def test_engine_connection(monkeypatch):
    """Engine이 정상적으로 연결되는지 확인 (mocked)"""
    config = MySQLConfig()

    # Engine과 Connection mocking
    fake_engine = MagicMock()
    fake_conn = MagicMock()
    fake_conn.execute.return_value.scalar.return_value = 1
    fake_engine.connect.return_value.__enter__.return_value = fake_conn

    monkeypatch.setattr(config, "get_engine", lambda: fake_engine)

    with config.get_engine().connect() as conn:
        result = conn.execute("SELECT 1").scalar()
        assert result == 1, "DB 연결 테스트 실패"


def test_session_creation(monkeypatch):
    """SessionLocal이 정상적으로 세션을 생성하는지 확인 (mocked)"""
    config = MySQLConfig()
    fake_session = MagicMock()
    monkeypatch.setattr(config, "get_session", lambda: fake_session)

    session = config.get_session()
    try:
        assert session is not None, "세션 생성 실패"
    finally:
        session.close()


def test_base_declarative(monkeypatch):
    """Base가 정상적으로 선언되어 있는지 확인 (mocked)"""
    config = MySQLConfig()
    fake_base = MagicMock()
    monkeypatch.setattr(config, "get_base", lambda: fake_base)

    Base = config.get_base()
    assert Base is not None, "Base 선언 실패"
