import asyncio
import logging
from datetime import datetime, timezone

import feedparser

from app.article import Article

logger = logging.getLogger(__name__)

MAX_RSS = 10

RSS_URL = "https://cointelegraph.com/rss"


async def fetch_rss() -> list[feedparser.FeedParserDict]:
    retries = 3
    timeout = 5.0
    retry_delay = 1.0

    logger.info(f"Fetching RSS feed: {RSS_URL}")
    for attempt in range(retries):
        try:
            rss = await asyncio.wait_for(
                asyncio.to_thread(feedparser.parse, RSS_URL), timeout=timeout
            )

            break
        except asyncio.TimeoutError:
            logger.warning(f"Timeout while fetching {RSS_URL} (attempt {attempt + 1})")
        except Exception as e:
            logger.error(
                f"Error while fetching {RSS_URL} (attempt {attempt + 1}): {e!s}"
            )
            raise

        if attempt < retries:
            logger.error(f"Retrying {RSS_URL} in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)

    else:
        logger.error(f"All {retries} attempts to fetch {RSS_URL} failed.")
        return []

    return rss.entries


async def fetch_articles() -> list[Article]:
    logger.info(f"Fetching RSS feed: {RSS_URL}")
    try:
        entries = await fetch_rss()

        articles = []
        counter = 0
        for entry in entries:
            if counter >= MAX_RSS:
                break

            published_dt = datetime.now(timezone.utc)
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published_dt = datetime(*entry.published_parsed[:6]).replace(  # pyright: ignore[reportArgumentType]
                        tzinfo=timezone.utc
                    )
                except Exception as e:
                    logger.warning(
                        f"Error parsing date for entry {entry.get('link')}: {e!s}"
                    )

            article = Article(
                title=entry.get("title", "No title"),  # pyright: ignore[reportArgumentType]
                link=entry.get("link", "#"),  # pyright: ignore[reportArgumentType]
                summary=entry.get("summary", ""),  # pyright: ignore[reportArgumentType]
                published_at=published_dt,
            )
            articles.append(article)

            counter += 1

        logger.info(f"Fetched {len(articles)} articles from {RSS_URL}")

        articles.sort(key=lambda x: x.published_at, reverse=True)

        return articles

    except Exception as e:
        logger.error(f"Error fetching RSS feed {RSS_URL}: {e!s}")
        return []
