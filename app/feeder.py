import asyncio
import logging
from datetime import datetime, timezone

import feedparser

from app.article import Article

logger = logging.getLogger(__name__)

MAX_RSS = 10

RSS_URL = "https://cointelegraph.com/rss"


async def fetch_articles() -> list[Article]:
    logger.info(f"Fetching RSS feed: {RSS_URL}")
    try:
        feed = await asyncio.to_thread(feedparser.parse, RSS_URL)

        articles = []
        for entry in feed.entries[:MAX_RSS]:
            published_dt = datetime.now(timezone.utc)
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published_dt = datetime(*entry.published_parsed[:6]).replace(
                        tzinfo=timezone.utc
                    )
                except Exception as e:
                    logger.warning(
                        f"Error parsing date for entry {entry.get('link')}: {e!s}"
                    )

            article = Article(
                title=entry.get("title", "No title"),
                link=entry.get("link", "#"),
                summary=entry.get("summary", ""),
                published_at=published_dt,
            )
            articles.append(article)

        logger.info(f"Fetched {len(articles)} articles from {RSS_URL}")

        articles.sort(key=lambda x: x.published_at, reverse=True)

        return articles

    except Exception as e:
        logger.error(f"Error fetching RSS feed {RSS_URL}: {e!s}")
        return []
