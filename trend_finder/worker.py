"""ARQ worker for periodic cache refreshes."""

import asyncio
from typing import Any

from arq import cron
from arq.connections import RedisSettings
from loguru import logger
from redis.asyncio import Redis

from trend_finder.cache import TrendCache
from trend_finder.config import Settings
from trend_finder.database.engine import (
    create_engine,
    create_session_factory,
    initialize_database,
)
from trend_finder.services.trend_service import TrendService
from trend_finder.sources import build_sources

settings = Settings()
sources = build_sources(settings.http_user_agent)


async def startup(ctx: dict[str, Any]) -> None:
    """Create shared worker resources and initialize the database."""
    engine = create_engine(settings.database_url)
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    await initialize_database(engine)
    await redis.ping()
    ctx["engine"] = engine
    ctx["redis"] = redis
    ctx["trend_service"] = TrendService(
        sources=sources,
        cache=TrendCache(redis),
        sessions=create_session_factory(engine),
    )


async def shutdown(ctx: dict[str, Any]) -> None:
    """Release worker resources."""
    redis: Redis | None = ctx.get("redis")
    if redis is not None:
        await redis.aclose()
    engine = ctx.get("engine")
    if engine is not None:
        await engine.dispose()


async def refresh_trends(ctx: dict[str, Any]) -> None:
    """Refresh configured country/source pairs every 30 minutes."""
    service: TrendService = ctx["trend_service"]
    jobs = [
        service.get_trends(source_key, country_code, force_refresh=True)
        for country_code in settings.refresh_country_codes
        for source_key in sources
    ]
    results = await asyncio.gather(*jobs, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logger.warning("Scheduled trend refresh failed: {}", result)
    logger.info("Scheduled refresh finished for {} source/country pairs", len(jobs))


class WorkerSettings:
    """ARQ worker configuration."""

    functions = [refresh_trends]
    cron_jobs = [cron(refresh_trends, minute={0, 30})]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
