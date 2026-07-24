import asyncio
import logging
from typing import Optional

import aiohttp
from aiohttp import ClientError
from bs4 import BeautifulSoup
from trafilatura import extract

logger = logging.getLogger(__name__)


class _NullContext:
    """Пустой асинхронный контекстный менеджер, когда семафор не нужен."""

    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, tb):
        pass


class Fetcher:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 10.0,
        timeout_connect: float = 5.0,
        timeout_read: float = 30.0,
        concurrency_limit: Optional[int] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

        self.timeout = aiohttp.ClientTimeout(
            total=None,
            connect=timeout_connect,
            sock_read=timeout_read,
        )

        if concurrency_limit is not None and concurrency_limit <= 0:
            raise ValueError("concurrency_limit должен быть > 0 или None")
        self._semaphore = (
            asyncio.Semaphore(concurrency_limit) if concurrency_limit else None
        )

        # Сессию НЕ создаём здесь: она будет создана в __aenter__
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "Fetcher":
        # Создаём сессию при входе в контекст
        self._session = aiohttp.ClientSession(timeout=self.timeout)
        logger.debug("ClientSession created")
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        # Корректно закрываем сессию при выходе из контекста
        if self._session is not None:
            await self._session.close()
            logger.debug("ClientSession closed")
            self._session = None

    async def fetch_html(self, url: str) -> str:
        if self._session is None:
            raise RuntimeError("Fetcher должен использоваться через async with")

        attempt = 0
        last_exc: Optional[Exception] = None

        while attempt <= self.max_retries:
            # Выбираем контекст: семафор или пустой менеджер
            semaphore_ctx = (
                self._semaphore if self._semaphore is not None else _NullContext()
            )

            async with semaphore_ctx:
                try:
                    async with self._session.get(url) as resp:
                        if 200 <= resp.status < 300:
                            html = await resp.text()
                            logger.info("Fetched %s (status %d)", url, resp.status)
                            return html
                        else:
                            logger.warning("Non-2xx status %d for %s", resp.status, url)
                            # Повторяем только для серверных ошибок (5xx)
                            if 500 <= resp.status < 600 and attempt < self.max_retries:
                                last_exc = RuntimeError(
                                    f"Server error {resp.status} for {url}"
                                )
                            else:
                                raise RuntimeError(f"HTTP {resp.status} for {url}")
                except (ClientError, asyncio.TimeoutError) as e:
                    logger.debug("Request error for %s: %s", url, e)
                    last_exc = e
                    if attempt == self.max_retries:
                        break
                    delay = min(self.base_delay * (2**attempt), self.max_delay)
                    logger.info(
                        "Retry %d/%d after %.2f s delay for %s",
                        attempt + 1,
                        self.max_retries,
                        delay,
                        url,
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue

        logger.error("All retries failed for %s", url)
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Unexpected failure while fetching HTML")

    @staticmethod
    def fetch_content(html: str) -> str | None:
        soup = BeautifulSoup(html, "lxml")

        post_body = soup.find("div", attrs={"data-testid": "post__body"})
        if not post_body:
            return

        text = extract(str(post_body))

        return text
