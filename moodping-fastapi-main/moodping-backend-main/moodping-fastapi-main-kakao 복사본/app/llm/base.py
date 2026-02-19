from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """
    모든 LLM 클라이언트가 구현해야 하는 공통 인터페이스.
    mood_analysis_service는 이 추상 클래스만 의존하므로
    LLM_PROVIDER를 바꿔도 서비스 코드 수정이 불필요합니다.
    """

    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> str | None:
        """
        LLM에 메시지를 보내고 응답 텍스트를 반환합니다.
        실패(타임아웃, API 오류 등) 시 None을 반환합니다.
        """
        ...
