"""Database engine and schema initialization."""

from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from trend_finder.database.models import Base


def create_engine(database_url: str) -> AsyncEngine:
    """Create an async engine and ensure a local SQLite parent folder exists."""
    if database_url.startswith("sqlite+aiosqlite:///"):
        sqlite_path = database_url.removeprefix("sqlite+aiosqlite:///")
        if sqlite_path and sqlite_path != ":memory:" and not sqlite_path.startswith("/"):
            Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    return create_async_engine(database_url, pool_pre_ping=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a session factory shared by handlers and background jobs."""
    return async_sessionmaker(engine, expire_on_commit=False)


async def initialize_database(engine: AsyncEngine) -> None:
    """Create tables for a fresh SQLite/PostgreSQL install."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
