from abc import ABC, abstractmethod
from typing import Dict, Any

class AuthenticationService(ABC):
    @abstractmethod
    def create_session(self, user_id: int, kakao_id: str) -> str:
        """
        주어진 사용자 정보로 JWT 세션 토큰을 생성합니다.
        """
        pass

    @abstractmethod
    def validate_session(self, token: str) -> Dict[str, Any]:
        """
        JWT 세션 토큰을 검증하고 페이로드를 반환합니다.
        유효하지 않으면 예외를 발생시킵니다.
        """
        pass
