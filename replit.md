# Trend Finder Bot

ربات تلگرام فارسی برای جمع‌آوری و نمایش ترندهای Google Trends و سیگنال‌های محبوبیت Reddit بر اساس کشور.

## Run & Operate

- `uv sync` — install Python dependencies
- `python main.py` — start Telegram polling
- `uv run arq trend_finder.worker.WorkerSettings` — start scheduled refresh worker
- `uv run pytest` — run Python tests
- `uv run ruff check .` — lint Python files
- `docker compose up --build -d` — start bot, Redis, and ARQ worker
- Required secret: `TELEGRAM_BOT_TOKEN`
- Optional env: `TREND_FINDER_DATABASE_URL`, `REDIS_URL`, `REFRESH_COUNTRIES`

## Stack

- Python 3.11+
- Telegram: Aiogram 3
- Settings: Pydantic Settings
- Database: SQLAlchemy 2 async, SQLite by default, PostgreSQL supported
- Cache and worker queue: Redis + ARQ
- Logging and retries: Loguru + tenacity

## Where things live

- `trend_finder/sources/` — source adapters and normalized trend data
- `trend_finder/handlers.py` — Telegram interaction flow
- `trend_finder/database/` — SQLAlchemy models and engine setup
- `trend_finder/worker.py` — periodic refresh worker
- `README.md` — setup, operation, source behavior, and quality commands

## Architecture decisions

- Google Trends RSS is the direct search-trend source; Reddit is labeled separately as community popularity, never as search volume.
- Redis is required at runtime; cache failures are surfaced instead of silently switching to a different cache.
- Every successful upstream refresh is stored as a point-in-time database snapshot.
- SQLite is the local default; setting `TREND_FINDER_DATABASE_URL` enables PostgreSQL through asyncpg.

## Product

Users choose a country and a provider in Telegram, then receive a ranked Persian-language list with provider links and source-specific metrics.

## User preferences

User-facing bot messages are in Persian.

## Gotchas

- Reddit scores are upvotes/engagement signals, not search counts.
- The bot and worker both need the same Redis and database URLs.
- Never commit `.env`; use Replit Secrets for the Telegram token.

## Pointers

- See `README.md` for setup, Docker Compose, tests, and the source adapter contract.
