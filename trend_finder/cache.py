"""Redis JSON cache with source-specific TTLs."""

import json

from redis.asyncio import Redis

from trend_finder.domain import TrendItem


class TrendCache:
    """Read/write cached provider results; Redis failures are not silently hidden."""

    def __init__(self, redis: Redis) -> None:
        """Bind the cache wrapper to an async Redis client."""
        self.redis = redis

    async def get(self, source: str, country_code: str) -> list[TrendItem] | None:
        """Return a cached collection, or None when its TTL has elapsed."""
        value = await self.redis.get(self._key(source, country_code))
        if value is None:
            return None
        payload = json.loads(value)
        return [TrendItem.from_dict(item) for item in payload]

    async def set(
        self,
        source: str,
        country_code: str,
        items: list[TrendItem],
        ttl_seconds: int,
    ) -> None:
        """Store a normalized collection with the provider's own TTL."""
        encoded = json.dumps([item.to_dict() for item in items], ensure_ascii=False)
        await self.redis.set(self._key(source, country_code), encoded, ex=ttl_seconds)

    @staticmethod
    def _key(source: str, country_code: str) -> str:
        """Build a stable, versionable key for a country/source pair."""
        return f"trend-finder:v1:{source}:{country_code.upper()}"
