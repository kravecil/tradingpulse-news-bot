"""
Module for fetching news from RSS feeds.
"""

import asyncio
import logging
from datetime import datetime, timezone

import feedparser

from feeding.article import Article
from feeding.sources.base import MAX_ARTICLES_PER_SOURCE, MAX_RSS_PER_SOURCE, BaseSource

logger = logging.getLogger(__name__)


class RSSSource(BaseSource):
    """
    A source for fetching news from RSS feeds.
    """

    name: str
    url: str

    async def fetch(self) -> list[Article]:
        logger.info(f"Fetching RSS feed: {self.url}")
        try:
            feed = await asyncio.to_thread(feedparser.parse, self.url)

            articles = []
            for entry in feed.entries[:MAX_RSS_PER_SOURCE]:
                # Parse published date using parsed struct_time
                published_dt = datetime.now(timezone.utc)
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        # Сначала создаём naive datetime, потом добавляем tzinfo
                        published_dt = datetime(*entry.published_parsed[:6]).replace(
                            tzinfo=timezone.utc
                        )
                    except Exception as e:
                        logger.warning(
                            f"Error parsing date for entry {entry.get('link')}: {e!s}"
                        )

                content = await self.fetch_content(entry.get("link", ""))

                article = Article(
                    title=entry.get("title", "No title"),
                    link=entry.get("link", "#"),
                    summary=entry.get("summary", ""),
                    published_at=published_dt,
                    source=self.name,
                    category="rss",
                    content=content,
                )
                articles.append(article)

            logger.info(f"Fetched {len(articles)} articles from {self.url}")

            articles.sort(key=lambda x: x.published_at, reverse=True)

            return articles[:MAX_ARTICLES_PER_SOURCE]

        except Exception as e:
            logger.error(f"Error fetching RSS feed {self.url}: {e!s}")
            return []

    async def fetch_content(self, url: str) -> str:
        raise NotImplementedError
