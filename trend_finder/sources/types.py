"""Shared provider protocol and structured upstream errors."""

from typing import Protocol

from trend_finder.domain import TrendItem


class TrendSourceError(RuntimeError):
    """Raised when a trend provider is unreachable or returns invalid data."""


class TrendSource(Protocol):
    """Contract implemented by each provider adapter."""

    key: str
    label: str
    ttl_seconds: int

    async def fetch(self, country_code: str) -> list[TrendItem]:
        """Fetch and normalize trends for the requested country."""
