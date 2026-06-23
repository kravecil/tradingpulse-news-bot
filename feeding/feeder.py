import asyncio
import logging
from typing import Any

from feeding.sources.base import BaseSource
from feeding.sources.rss import RSSSource
from feeding.sources_list import RSS_SOURCES
from feeding.article import Article

logger = logging.getLogger(__name__)


class TradingPulseFeeder:
    def __init__(self) -> None:
        self.sources = self._init_sources()

    def _init_sources(self) -> list[BaseSource]:
        """Initialize and return a list of all configured news sources."""
        sources: list[BaseSource] = []

        # Add RSS sources
        for source in RSS_SOURCES:
            sources.append(source())

        return sources

    async def fetch_all_news(self) -> list[Article]:
        """
        Fetch news articles from all sources concurrently.

        Returns:
            A deduplicated and sorted list of news articles.
        """
        logger.info("Fetching news from all sources...")
        all_articles: list[Article] = []

        # Create a task for each source's fetch method
        tasks = [source.fetch() for source in self.sources]

        # Execute all fetch tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results and handle any exceptions
        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                logger.error(f"Error fetching from source {self.sources[i]}: {result}")
            else:
                all_articles.extend(result)

        # Remove duplicates based on the link
        seen_links = set()
        unique_articles: list[Article] = []
        for article in all_articles:
            if article.link not in seen_links:
                seen_links.add(article.link)
                unique_articles.append(article)

        logger.info(f"Fetched {len(unique_articles)} unique articles.")
        return unique_articles
