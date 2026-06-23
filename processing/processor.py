"""
Module for processing and analyzing news articles using AI (Yandex GPT).
"""

import asyncio
import logging

import aiohttp

from config.settings import settings
from feeding.article import Article

logger = logging.getLogger(__name__)

NEWS_FETCH_INTERVAL_MINUTES: int = 30
MAX_NEWS_PER_POST: int = 5
MIN_WORDS_FOR_SUMMARY: int = 50


class TradingPulseProcessor:
    """
    A processor that uses Yandex GPT to summarize, translate, and analyze news articles.
    """

    def __init__(self) -> None:
        """
        Initialize the NewsProcessor with the configured AI service.
        """
        self.session: aiohttp.ClientSession | None = None

        self._process_func = self._process_with_yandex
        # self._process_func = self._process_with_gigachat

        self.yandex_api_key = settings.yandex_api_key.get_secret_value()
        self.yandex_folder_id = settings.yandex_folder_id

    async def __aenter__(self):
        """
        Async context manager entry. Creates a shared aiohttp session.
        """
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit. Closes the shared aiohttp session.
        """
        if self.session:
            await self.session.close()
            self.session = None

    async def process(self, articles: list[Article]) -> list[Article]:
        """
        Process a list of news articles using the configured AI service.
        This includes summarization, translation to Russian, and sentiment analysis.

        Args:
            articles (list[dict[str, Any]]): The list of articles to process.

        Returns:
            A list of processed articles with added AI-generated fields.
        """
        if not self.session:
            # If not used as a context manager, create a temporary session
            async with self:
                return await self._process_batch(articles)

        return await self._process_batch(articles)

    async def _process_batch(self, articles: list[Article]) -> list[Article]:
        """Process a batch of articles concurrently using the selected AI function."""
        # Фильтруем короткие статьи заранее
        tasks = []
        skipped_articles = {}

        for i, article in enumerate(articles):
            content = f"{article.title} {article.summary}"
            if len(content.split()) < MIN_WORDS_FOR_SUMMARY:
                logger.info(f"Skipping {article.title} due to short content.")
                skipped_articles[i] = (
                    article  # сохраняем индекс для правильного порядка
                )
            else:
                # Создаём задачу для каждой статьи
                task = self._process_func(article)
                tasks.append(task)

        # Выполняем все задачи параллельно
        try:
            processed_results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error during parallel processing: {e!s}")
            processed_results = []

        # Собираем результаты в правильном порядке
        processed_articles = []
        result_iter = iter(processed_results)

        for i in range(len(articles)):
            if i in skipped_articles:
                processed_articles.append(skipped_articles[i])
            else:
                result = next(result_iter)
                if isinstance(result, BaseException):
                    logger.error(f"Error processing article: {result}")
                    # В случае ошибки возвращаем оригинальную статью
                    processed_articles.append(articles[i])
                else:
                    processed_articles.append(result)

        return processed_articles

    async def _process_with_yandex(self, article: Article) -> Article:
        """
        Process a single article using Yandex GPT.

        Args:
            article (Article): The article to process.

        Returns:
            The processed article with 'summary_ru' and 'sentiment' fields added.
        """

        if self.session is None:
            logger.error(
                "Session is not initialized. Please use the processor as a context manager."
            )
            return article

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Authorization": f"Api-Key {self.yandex_api_key}",
            "x-folder-id": self.yandex_folder_id,
            "Content-Type": "application/json",
        }

        # Prepare the prompt for Yandex GPT
        content = f"{article.title}\n\n{article.summary}\n\n{article.content}"
        prompt = (
            "Проанализируй новость как финансовый аналитик, переведи на русский язык."
            "Текст подготовь для Telegram-канала c parse mode = html, сделай краткое резюме и выдели ключевые моменты."
            f" Также определи общий сентимент: позитивный, негативный или нейтральный.\n\nНовость:\n{content}"
        )

        payload = {
            "modelUri": f"gpt://{self.yandex_folder_id}/yandexgpt/latest",
            "completionOptions": {"temperature": 0.5, "maxTokens": "500"},
            "messages": [
                {
                    "role": "system",
                    "text": "Ты — помощник, который анализирует новости из мира криптовалют.",
                },
                {"role": "user", "text": prompt},
            ],
        }

        try:
            async with self.session.post(
                url, headers=headers, json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    # Extract the AI-generated text
                    text = result["result"]["alternatives"][0]["message"]["text"]

                    # Simple parsing to extract summary and sentiment
                    # This could be improved with a more structured prompt and parsing
                    lines = text.strip().split("\n")
                    summary_ru = ""
                    sentiment = "neutral"

                    for line in lines:
                        line_lower = line.lower()
                        if "сентимент" in line_lower or "настроение" in line_lower:
                            if "позитив" in line_lower:
                                sentiment = "positive"
                            elif "негатив" in line_lower:
                                sentiment = "negative"
                        else:
                            # Assume the first non-sentiment line is the summary
                            if not summary_ru and line.strip():
                                summary_ru = line.strip()

                    # Add the new fields to the article
                    article.summary_ru = summary_ru
                    article.sentiment = sentiment
                    logger.info(f"Processed article with Yandex GPT: {article.title}")

                else:
                    logger.error(f"Yandex GPT API returned status {response.status}")
        except Exception as e:
            logger.error(f"Error calling Yandex GPT for '{article.title}': {e!s}")

        return article
