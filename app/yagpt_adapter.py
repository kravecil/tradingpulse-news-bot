import logging
from typing import Self

from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import ChatCompletion, Choice

from app.settings import settings

logger = logging.getLogger(__name__)


class YandexGPTAdapter:
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        self._model = f"gpt://{settings.yandex_folder_id}/{settings.openai_model}"

    async def __aenter__(self) -> Self:
        client = AsyncOpenAI(
            api_key=settings.yandex_api_key.get_secret_value(),
            base_url=settings.openai_base_url,
            project=settings.yandex_folder_id,
            max_retries=3,
            timeout=120,
        )
        self._client = client

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Yandex GPT client closed")

    async def generate(
        self, prompt: str, instructions: str | None = None
    ) -> str | None:
        if not self._client:
            raise ValueError("Yandex GPT client is not initialized")

        try:
            messages = [ChatCompletionUserMessageParam(role="user", content=prompt)]

            user_message = ChatCompletionUserMessageParam(role="user", content=prompt)
            if instructions:
                messages = [
                    user_message,
                    ChatCompletionSystemMessageParam(
                        role="system", content=instructions
                    ),
                ]
            else:
                messages = [user_message]
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.3,
                max_tokens=1500,
                n=1,
                timeout=120,
            )

            return self._extract_text(completion)
        except Exception as e:
            logger.error(f"Error calling Yandex GPT: {e!s}")
            raise

    @staticmethod
    def _extract_text(completion: ChatCompletion) -> str | None:
        for choice in completion.choices:
            if isinstance(choice, Choice):
                return choice.message.content

        return None
