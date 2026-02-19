import logging
import anthropic
from .base import BaseLLMClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class ClaudeClient(BaseLLMClient):
    """claude-haiku-4-5-20251001 기반 Anthropic Claude 클라이언트."""

    def __init__(self):
        settings = get_settings()
        self._client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.llm_timeout_seconds,
        )
        self._model = settings.claude_model
        self._max_tokens = settings.llm_max_tokens
        self._temperature = settings.llm_temperature

    async def complete(self, system_prompt: str, user_prompt: str) -> str | None:
        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text
        except anthropic.APIError as e:
            logger.error("Claude API 오류: %s", e)
            return None
        except Exception as e:
            logger.error("Claude 호출 실패: %s", e)
            return None
