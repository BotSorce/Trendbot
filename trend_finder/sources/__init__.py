"""Trend provider adapters."""

from trend_finder.sources.google_trends import GoogleTrendsSource
from trend_finder.sources.reddit import RedditPopularSource
from trend_finder.sources.types import TrendSource


def build_sources(user_agent: str = "TrendFinderBot/1.0") -> dict[str, TrendSource]:
    """Build source adapters with the configured HTTP user agent."""
    return {
        GoogleTrendsSource.key: GoogleTrendsSource(user_agent),
        RedditPopularSource.key: RedditPopularSource(user_agent),
    }


SOURCES = build_sources()

__all__ = ["SOURCES", "TrendSource", "build_sources"]
