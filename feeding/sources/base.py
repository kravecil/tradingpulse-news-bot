from abc import ABC, abstractmethod

from feeding.article import Article

MAX_RSS_PER_SOURCE = 50
MAX_ARTICLES_PER_SOURCE = 1

TIMEOUT = 5


class BaseSource(ABC):
    """
    Abstract base class for a news source.
    """

    @abstractmethod
    async def fetch(self) -> list[Article]:
        """
        Fetch news articles from the source.

        Returns:
            A list of news articles as dictionaries.
        """
        pass
