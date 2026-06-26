import logging

from app.article import Article
from app.yagpt_adapter import YandexGPTAdapter

logger = logging.getLogger(__name__)


class PostGenerator:
    def __init__(self, adapter: YandexGPTAdapter) -> None:
        # TODO @me: move `instructions` and `prompt` to external files
        self._instructions = (
            "Ты — финансовый аналитик и администратор Telegram-канала о криптовалютах.\n\n"
            "Твоя задача — написать уникальный и увлекательный пост для Telegram на основе внешней новости.\n\n"
            "Правила:\n"
            "- Пиши текст, который **никогда не повторяет** формулировки из запроса или ссылки.\n"
            "- Не упоминай, что ты переводишь или что исходник где-то есть.\n"
            "- Не используй фразы вроде «по сообщению…», «сообщается, что…», «источник…».\n"
            "- Не дублируй ни слово, ни фразу из исходного запроса или ссылки.\n"
            "- Пост должен быть цельным и законченным.\n"
            "- Язык: русский."
        )

        self._prompt = (
            "Вот новость для анализа: {url}\n\n"
            "Требуется:\n"
            "1. Коротко описать суть новости на русском.\n"
            "2. Дать краткий финансовый анализ (влияние, перспективы).\n"
            "3. Использовать актуальные Telegram-эмодзи.\n"
            "4. В конце — 2–3 релевантных хэштега (например, #BTC #CryptoNews).\n"
            "5. Не добавляй преамбулы вроде «Вот анализ» или «Сообщается, что…».\n"
            "6. Не копируй исходный текст и не упоминай его источник.\n"
            "7. Текст должен звучать как самостоятельный пост — не как перевод или пересказ."
        )

        self._adapter = adapter

    async def process(self, articles: list[Article]) -> Article:
        latest_article = self._get_latest_article(articles)

        if latest_article is None:
            raise ValueError("No articles to process")

        prompt = self._prompt.format(url=latest_article.link)

        content = await self._adapter.generate(
            prompt=prompt, instructions=self._instructions
        )

        latest_article.content = content

        return latest_article

    @staticmethod
    def _get_latest_article(articles: list[Article]) -> Article | None:
        return next(iter(articles), None)
