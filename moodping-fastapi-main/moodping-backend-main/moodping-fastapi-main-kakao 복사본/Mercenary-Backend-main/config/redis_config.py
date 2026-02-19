import redis
from redis import Redis
from config.settings import get_settings


class RedisConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            settings = get_settings()

            cls._instance = super().__new__(cls)

            cls._instance._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                max_connections=10
            )

            cls._instance._client = Redis(connection_pool=cls._instance._pool)

            try:
                cls._instance._client.ping()
            except redis.ConnectionError as e:
                raise RuntimeError(f"Redis 연결 실패: {e}")

        return cls._instance

    def get_client(self) -> Redis:
        return self._client
