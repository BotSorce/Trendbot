"""Tests for safe Persian Telegram output."""

from trend_finder.domain import TrendItem
from trend_finder.handlers import render_trends


def test_render_trends_escapes_untrusted_provider_text() -> None:
    """Provider content is escaped before it is sent as Telegram HTML."""
    items = [
        TrendItem(
            source="reddit",
            country_code="US",
            title="<script>alert(1)</script>",
            url="https://www.reddit.com/r/example/1",
            metric="10 امتیاز",
            position=1,
        )
    ]

    message = render_trends(items, "Reddit", "ایالات متحده")

    assert "<script>" not in message
    assert "&lt;script&gt;" in message
    assert 'href="https://www.reddit.com/r/example/1"' in message
    assert "فیلتر منطقه ممکن است" in message


def test_render_trends_does_not_link_non_http_urls() -> None:
    """Only HTTP(S) provider URLs become Telegram anchors."""
    item = TrendItem(
        source="google_trends",
        country_code="US",
        title="Search term",
        url="javascript:alert(1)",
        position=1,
    )

    message = render_trends([item], "Google Trends", "ایالات متحده")

    assert "<a href=" not in message
    assert "Search term" in message
