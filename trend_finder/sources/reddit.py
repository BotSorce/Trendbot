"""Reddit popular-post adapter, used as a community trend signal."""

import asyncio
import re
from html import unescape

import aiohttp
import feedparser
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from trend_finder.domain import TrendItem
from trend_finder.sources.types import TrendSourceError

_HTML_TAG = re.compile(r"<[^>]+>")


class RedditPopularSource:
    """Fetch Reddit's public popular-post RSS and normalize its entries."""

    key = "reddit"
    label = "Reddit"
    ttl_seconds = 600
    endpoint = "https://www.reddit.com/r/popular/top/.rss"

    def __init__(self, user_agent: str = "TrendFinderBot/1.0") -> None:
        """Create a Reddit adapter with a descriptive user agent."""
        self.user_agent = user_agent

    @retry(
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=0.5, max=4),
        reraise=True,
    )
    async def _download(self, country_code: str) -> str:
        """Request Reddit's public popular RSS feed with a country hint."""
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(
            timeout=timeout,
            headers={"User-Agent": self.user_agent, "Accept": "application/rss+xml"},
        ) as session:
            async with session.get(
                self.endpoint,
                params={"t": "day", "limit": "20", "geo": country_code},
            ) as response:
                if response.status == 429 or response.status >= 500:
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message="Reddit temporarily unavailable",
                    )
                if response.status >= 400:
                    raise TrendSourceError(f"Reddit returned HTTP {response.status}")
                return await response.text()

    async def fetch(self, country_code: str) -> list[TrendItem]:
        """Fetch Reddit entries without claiming unavailable engagement metrics."""
        try:
            body = await self._download(country_code.upper())
        except TrendSourceError:
            raise
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise TrendSourceError("اتصال به Reddit برقرار نشد.") from exc

        items = await asyncio.to_thread(parse_feed, body, country_code.upper())
        if not items:
            raise TrendSourceError("Reddit در حال حاضر موردی برای نمایش برنگرداند.")
        return items


def parse_feed(body: str, country_code: str = "US") -> list[TrendItem]:
    """Parse public Reddit RSS entries into normalized community signals."""
    parsed = feedparser.parse(body)
    items: list[TrendItem] = []
    for position, entry in enumerate(parsed.entries[:20], start=1):
        title = str(entry.get("title", "")).strip()
        if not title:
            continue
        raw_summary = str(entry.get("summary", ""))
        summary = " ".join(unescape(_HTML_TAG.sub(" ", raw_summary)).split())
        items.append(
            TrendItem(
                source=RedditPopularSource.key,
                country_code=country_code.upper(),
                title=title,
                url=str(entry.get("link", "")),
                summary=summary,
                metric="محبوبیت جامعه",
                position=position,
            )
        )
    return items
