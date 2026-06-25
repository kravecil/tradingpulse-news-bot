import logging

from app.article import Article
from app.yagpt_adapter import YandexGPTAdapter

logger = logging.getLogger(__name__)


class PostGenerator:
    def __init__(self, adapter: YandexGPTAdapter) -> None:
        # TODO @me: move `instructions` and `prompt` to external files
        self._instructions = "Ты — финансовый аналитик и администратор Telegram-канала в области криптовалютных новостей."
        self._prompt = (
            "Прочти новость по ссылке: {url}\n\n"
            "Проанализируй новость как финансовый аналитик, переведи на русский язык."
            "Подготовь краткий анализ в виде поста для своего канала."
            "Используй поддерживаемые Telegram emoji."
            "В заключении поста пропиши актуальные хэштеги."
            "Не добавляй никаких примечаний, предназначенных для администратора."
            "Новость представь так, как будто ты первоисточник"
            "Не отображай первоисточник новости"
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
