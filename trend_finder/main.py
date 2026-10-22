"""Bot startup and graceful resource shutdown."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger
from redis.asyncio import Redis

from trend_finder.cache import TrendCache
from trend_finder.config import Settings
from trend_finder.database.engine import (
    create_engine,
    create_session_factory,
    initialize_database,
)
from trend_finder.handlers import router
from trend_finder.logging_config import configure_logging
from trend_finder.services.trend_service import TrendService
from trend_finder.sources import build_sources


async def main() -> None:
    """Initialize database, Redis, and polling bot; close resources on exit."""
    settings = Settings()
    configure_logging(settings.log_dir, settings.log_level)
    engine = create_engine(settings.database_url)
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    bot = Bot(
        token=settings.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher(storage=MemoryStorage())

    try:
        await initialize_database(engine)
        await redis.ping()
        sessions = create_session_factory(engine)
        dispatcher["trend_service"] = TrendService(
            sources=build_sources(settings.http_user_agent),
            cache=TrendCache(redis),
            sessions=sessions,
        )
        dispatcher.include_router(router)
        logger.info("Trend Finder bot started")
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
    finally:
        await bot.session.close()
        await redis.aclose()
        await engine.dispose()
        logger.info("Trend Finder bot stopped")
