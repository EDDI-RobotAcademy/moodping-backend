import logging
from openai import AsyncOpenAI, APIError
from .base import BaseLLMClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    """gpt-4.1-mini 기반 OpenAI 클라이언트."""

    def __init__(self):
        settings = get_settings()
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.llm_timeout_seconds,
        )
        self._model = settings.openai_model
        self._max_tokens = settings.llm_max_tokens
        self._temperature = settings.llm_temperature

    async def complete(self, system_prompt: str, user_prompt: str) -> str | None:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self._max_tokens,
                temperature=self._temperature,
            )
            return response.choices[0].message.content
        except APIError as e:
            logger.error("OpenAI API 오류: %s", e)
            return None
        except Exception as e:
            logger.error("OpenAI 호출 실패: %s", e)
            return None
