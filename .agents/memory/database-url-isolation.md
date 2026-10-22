---
name: Database URL isolation
description: Avoid accidentally binding this bot to a workspace-level database URL.
---

Use `TREND_FINDER_DATABASE_URL` to configure this bot's SQLAlchemy async database. Leave it unset for the documented SQLite default; set it explicitly to an `postgresql+asyncpg://` URL when choosing PostgreSQL.

**Why:** The Replit workspace may already expose `DATABASE_URL` for another service, and that value can point at a synchronous PostgreSQL driver. Letting it override the bot's SQLite default caused worker startup to fail and could connect this bot to an unrelated database.

**How to apply:** Preserve the app-specific variable in the Pydantic settings, `.env.example`, Docker Compose, and setup docs. Do not reuse the workspace's generic database URL unless the user explicitly chooses that database for this bot.
