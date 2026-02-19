from datetime import timedelta
import uuid

from authentication.service.authentication_service import AuthenticationService
from redis_cache.repository.redis_cache_repository_impl import RedisCacheRepositoryImpl


class AuthenticationServiceImpl(AuthenticationService):
    _instance = None

    SESSION_TTL = timedelta(hours=1)
    TEMP_SESSION_TTL = timedelta(minutes=5)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.redis = RedisCacheRepositoryImpl.get_instance()
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_session(self, account_id: int, kakao_access_token: str) -> str:
        user_token = str(uuid.uuid4())

        # Redis: userToken -> account_id
        self.redis.set_key_and_value(
            key=f"session:{user_token}",
            value=account_id,
            ttl=self.SESSION_TTL
        )

        # Redis: account_id -> kakao_access_token
        self.redis.set_key_and_value(
            key=f"account:{account_id}:kakao_token",
            value=kakao_access_token,
            ttl=self.SESSION_TTL
        )

        return user_token

    def validate_session(self, user_token: str) -> int | None:
        account_id = self.redis.get_value_by_key(
            f"session:{user_token}",
            int
        )

        return account_id

    def create_temp_session(self, kakao_access_token: str) -> str:
        temp_token = str(uuid.uuid4())
        self.redis.set_key_and_value(
            key=f"temp_session:{temp_token}",
            value=kakao_access_token,
            ttl=self.TEMP_SESSION_TTL
        )
        return temp_token

    def delete_temp_session(self, temp_token: str):
        self.redis.delete_by_key(f"temp_session:{temp_token}")

    def get_temp_session(self, temp_token: str) -> str | None:
        return self.redis.get_value_by_key(f"temp_session:{temp_token}", str)