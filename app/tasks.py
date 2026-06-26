import logging

from app.bot import create_bot
from app.db import ArticleRepository, DBManager
from app.feeder import fetch_articles
from app.post_generator import PostGenerator
from app.yagpt_adapter import YandexGPTAdapter

logger = logging.getLogger(__name__)


async def publish():
    logger.info("Starting publish task")

    fetched_articles = await fetch_articles()
    async with DBManager() as manager:
        repo = ArticleRepository(manager)

        article_guids = [article.guid for article in fetched_articles]

        db_articles = await repo.get_articles_by_guids(article_guids)
        db_article_guids = [article.guid for article in db_articles]

    filtered_articles = [
        article for article in fetched_articles if article.guid not in db_article_guids
    ]

    articles = sorted(filtered_articles, key=lambda x: x.published_at, reverse=True)

    bot = create_bot()

    async with YandexGPTAdapter() as adapter:
        generator = PostGenerator(adapter)

        for article in articles:
            post = await generator.process([article])
            await bot.send(post.content)

    logger.info("Publish task completed")
