import logging
from typing import Self

from openai import AsyncOpenAI
from openai.types.responses import Response, ResponseOutputMessage, ResponseOutputText

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
            response = await self._client.responses.create(
                model=self._model,
                instructions=instructions,
                input=prompt,
                temperature=0.5,
                max_output_tokens=1000,
            )

            return self._extract_text(response)
        except Exception as e:
            logger.error(f"Error calling Yandex GPT: {e!s}")
            raise

    @staticmethod
    def _extract_text(response: Response) -> str | None:
        for output in response.output:
            if isinstance(output, ResponseOutputMessage):
                for content in output.content:
                    if isinstance(content, ResponseOutputText):
                        return content.text

        return None
