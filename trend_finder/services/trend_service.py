"""Coordinate cache lookup, provider fetch, and snapshot persistence."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from trend_finder.cache import TrendCache
from trend_finder.database.models import TrendRecord, TrendSnapshot
from trend_finder.domain import TrendItem
from trend_finder.sources.types import TrendSource


class TrendService:
    """Fetch trends while keeping provider, cache, and persistence concerns separate."""

    def __init__(
        self,
        sources: dict[str, TrendSource],
        cache: TrendCache,
        sessions: async_sessionmaker[AsyncSession],
    ) -> None:
        """Create a service with provider adapters, Redis cache, and DB sessions."""
        self.sources = sources
        self.cache = cache
        self.sessions = sessions

    async def get_trends(
        self,
        source_key: str,
        country_code: str,
        *,
        force_refresh: bool = False,
    ) -> list[TrendItem]:
        """Return cached data or fetch, persist, then cache a fresh collection."""
        source = self.sources.get(source_key)
        if source is None:
            raise ValueError(f"Unknown trend source: {source_key}")
        country_code = country_code.upper()

        if not force_refresh:
            cached = await self.cache.get(source.key, country_code)
            if cached is not None:
                return cached

        items = await source.fetch(country_code)
        await self._persist(source.key, country_code, items)
        await self.cache.set(source.key, country_code, items, source.ttl_seconds)
        return items

    async def _persist(self, source_key: str, country_code: str, items: list[TrendItem]) -> None:
        """Store each successful upstream response as an immutable snapshot."""
        async with self.sessions() as session:
            snapshot = TrendSnapshot(source=source_key, country_code=country_code)
            snapshot.items = [
                TrendRecord(
                    position=item.position,
                    title=item.title,
                    url=item.url,
                    summary=item.summary,
                    metric=item.metric,
                    metric_value=item.metric_value,
                )
                for item in items
            ]
            session.add(snapshot)
            await session.commit()
