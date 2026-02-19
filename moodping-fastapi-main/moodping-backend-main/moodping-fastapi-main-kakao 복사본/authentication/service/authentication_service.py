from abc import ABC, abstractmethod


class AuthenticationService(ABC):
    """JWT 기반 세션 생성/검증 인터페이스."""

    @abstractmethod
    def create_session(self, user_id: int, kakao_id: str) -> str:
        """세션(JWT) 생성. 반환: access token 문자열."""
        pass

    @abstractmethod
    def validate_session(self, token: str) -> int | None:
        """토큰 검증. 유효하면 user_id, 아니면 None."""
        pass

    @abstractmethod
    def get_payload(self, token: str) -> dict | None:
        """토큰 payload 반환 (검증 실패 시 None)."""
        pass
