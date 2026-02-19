import logging
from functools import lru_cache
from .base import BaseLLMClient
from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm_client() -> BaseLLMClient:
    """
    LLM_PROVIDER 환경변수를 읽어 해당 구현체를 반환합니다.
    lru_cache로 앱 생명주기 동안 단 하나의 인스턴스만 생성합니다.

    .env 설정:
        LLM_PROVIDER=openai   → OpenAIClient  (gpt-4.1-mini)
        LLM_PROVIDER=gemini   → GeminiClient  (gemini-3-flash-preview)
        LLM_PROVIDER=claude   → ClaudeClient  (claude-haiku-4-5-20251001)
    """
    provider = get_settings().llm_provider.lower().strip()
    logger.info("LLM 제공자: %s", provider)

    if provider == "openai":
        from .openai_client import OpenAIClient
        return OpenAIClient()
    elif provider == "gemini":
        from .gemini_client import GeminiClient
        return GeminiClient()
    elif provider == "claude":
        from .claude_client import ClaudeClient
        return ClaudeClient()
    else:
        raise ValueError(
            f"지원하지 않는 LLM_PROVIDER: '{provider}'. "
            f"openai | gemini | claude 중 하나를 선택하세요."
        )
