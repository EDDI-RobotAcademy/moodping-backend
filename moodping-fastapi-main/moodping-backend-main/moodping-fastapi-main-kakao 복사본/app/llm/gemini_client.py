import asyncio
import logging
import google.generativeai as genai
from .base import BaseLLMClient
from app.config import get_settings

logger = logging.getLogger(__name__)


class GeminiClient(BaseLLMClient):
    """gemini-2.5-flash 기반 Google Gemini 클라이언트."""

    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self._model_name  = settings.gemini_model
        self._max_tokens  = settings.llm_max_tokens
        self._temperature = settings.llm_temperature
        self._timeout     = settings.llm_timeout_seconds
        logger.info(
            "GeminiClient 초기화 — model=%s, max_tokens=%d, timeout=%.1fs",
            self._model_name, self._max_tokens, self._timeout,
        )

    async def complete(self, system_prompt: str, user_prompt: str) -> str | None:
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        # GenerationConfig를 요청마다 생성 (모델 초기화 캐시 문제 방지)
        generation_config = genai.GenerationConfig(
            max_output_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        model = genai.GenerativeModel(
            model_name=self._model_name,
            generation_config=generation_config,
        )

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, combined_prompt),
                timeout=self._timeout,
            )

            # finish_reason 로깅으로 왜 멈췄는지 확인
            candidate = response.candidates[0] if response.candidates else None
            if candidate:
                finish_reason = candidate.finish_reason
                usage = getattr(response, "usage_metadata", None)
                logger.info("Gemini finish_reason=%s, usage=%s", finish_reason, usage)
                if str(finish_reason) not in ("FinishReason.STOP", "1", "STOP"):
                    logger.warning("Gemini 비정상 종료: finish_reason=%s", finish_reason)

            return response.text

        except asyncio.TimeoutError:
            logger.error("Gemini 호출 타임아웃 (%.1fs)", self._timeout)
            return None
        except Exception as e:
            logger.error("Gemini 호출 실패: %s", e)
            return None
