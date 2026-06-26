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

        article_pub_dates = [article.published_at for article in fetched_articles]  # type: ignore

        db_articles = await repo.get_articles_by_pub_date(article_pub_dates)
        db_article_pub_dates = [article.published_at for article in db_articles]

        filtered_articles = [
            article
            for article in fetched_articles
            if article.published_at not in db_article_pub_dates
        ]

        articles = sorted(filtered_articles, key=lambda x: x.published_at)

        bot = create_bot()

        async with YandexGPTAdapter() as adapter:
            generator = PostGenerator(adapter)

            for article in articles:
                link = str(article.link)

                try:
                    post = await generator.process([article])
                    await bot.send(post.content)

                    await repo.create_article(
                        published_at=article.published_at, link=link
                    )
                except Exception as e:
                    logger.error(
                        f"Error while processing article {link}: {e}",
                        exc_info=True,
                    )

    logger.info("Publish task completed")
