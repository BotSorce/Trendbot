"""Google Trends RSS adapter."""

import asyncio
import re
from typing import Any

import aiohttp
import feedparser
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from trend_finder.domain import TrendItem
from trend_finder.sources.types import TrendSourceError

_TRAFFIC_PATTERN = re.compile(r"([\d,.]+)\s*([KMB]?)", re.IGNORECASE)


def parse_traffic(value: str) -> float | None:
    """Convert Google's approximate traffic labels such as 20K+ to a number."""
    match = _TRAFFIC_PATTERN.search(value.replace("+", "").strip())
    if not match:
        return None
    number = float(match.group(1).replace(",", ""))
    multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    return number * multiplier.get(match.group(2).upper(), 1)


class GoogleTrendsSource:
    """Retrieve Google's public Trending Now feed for a country."""

    key = "google_trends"
    label = "Google Trends"
    ttl_seconds = 300
    base_url = "https://trends.google.com/trending/rss"

    def __init__(self, user_agent: str = "TrendFinderBot/1.0") -> None:
        """Create a source adapter with a descriptive HTTP user agent."""
        self.user_agent = user_agent

    @retry(
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=0.5, max=4),
        reraise=True,
    )
    async def _download(self, country_code: str) -> str:
        """Download the RSS feed, retrying transient network and server errors."""
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(
            timeout=timeout,
            headers={"User-Agent": self.user_agent, "Accept": "application/rss+xml"},
        ) as session:
            async with session.get(self.base_url, params={"geo": country_code}) as response:
                if response.status == 429 or response.status >= 500:
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message="Google Trends temporarily unavailable",
                    )
                if response.status >= 400:
                    raise TrendSourceError(f"Google Trends returned HTTP {response.status}")
                return await response.text()

    async def fetch(self, country_code: str) -> list[TrendItem]:
        """Fetch and normalize current Google Trends entries."""
        try:
            body = await self._download(country_code.upper())
        except TrendSourceError:
            raise
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise TrendSourceError("اتصال به Google Trends برقرار نشد.") from exc

        parsed = await asyncio.to_thread(feedparser.parse, body)
        items: list[TrendItem] = []
        for position, entry in enumerate(parsed.entries[:20], start=1):
            title = str(entry.get("title", "")).strip()
            if not title:
                continue
            traffic = str(entry.get("ht_approx_traffic", entry.get("approx_traffic", ""))).strip()
            summary = str(entry.get("summary", "")).strip()
            items.append(
                TrendItem(
                    source=self.key,
                    country_code=country_code.upper(),
                    title=title,
                    url=str(entry.get("link", "")),
                    summary=summary,
                    metric=f"حدود {traffic} جست‌وجو" if traffic else "",
                    metric_value=parse_traffic(traffic),
                    position=position,
                )
            )
        if not items:
            raise TrendSourceError("Google Trends در حال حاضر موردی برای نمایش برنگرداند.")
        return items


def parse_feed(body: str, country_code: str = "US") -> list[TrendItem]:
    """Parse a supplied RSS body; exposed separately for deterministic tests."""
    parsed: Any = feedparser.parse(body)
    results: list[TrendItem] = []
    for position, entry in enumerate(parsed.entries[:20], start=1):
        title = str(entry.get("title", "")).strip()
        if title:
            traffic = str(entry.get("ht_approx_traffic", entry.get("approx_traffic", ""))).strip()
            results.append(
                TrendItem(
                    source=GoogleTrendsSource.key,
                    country_code=country_code.upper(),
                    title=title,
                    url=str(entry.get("link", "")),
                    summary=str(entry.get("summary", "")).strip(),
                    metric=f"حدود {traffic} جست‌وجو" if traffic else "",
                    metric_value=parse_traffic(traffic),
                    position=position,
                )
            )
    return results
