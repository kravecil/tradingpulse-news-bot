import aiohttp
from bs4 import BeautifulSoup

from feeding.sources.base import TIMEOUT
from feeding.sources.rss import RSSSource


class CointelegraphSource(RSSSource):
    name = "CoinTelegraph"
    url = "https://cointelegraph.com/rss"

    async def fetch_content(self, url: str) -> str:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(TIMEOUT)
        ) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return ""
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Try to find post__body
                body_div = soup.find("div", attrs={"data-testid": "post__body"})

                if not body_div:
                    raise ValueError(
                        f"Could not find post__body for {url}. "
                        "Check the HTML structure."
                    )

                return body_div.get_text(separator="\n")
                # return "\n".join(line.strip() for line in body_div.stripped_strings)
