"""Unit tests for provider normalization."""

from trend_finder.sources.google_trends import parse_feed, parse_traffic
from trend_finder.sources.reddit import RedditPopularSource
from trend_finder.sources.reddit import parse_feed as parse_reddit_feed


def test_parse_google_trends_rss_item() -> None:
    """Google RSS values should normalize into a country-aware item."""
    rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel><item>
      <title>Example search</title>
      <link>https://trends.google.com/trends/explore?q=example</link>
      <ht:approx_traffic xmlns:ht="https://trends.google.com/trending/rss">20K+</ht:approx_traffic>
      <description>Related story</description>
    </item></channel></rss>"""

    items = parse_feed(rss, country_code="ir")

    assert len(items) == 1
    assert items[0].title == "Example search"
    assert items[0].country_code == "IR"
    assert items[0].metric_value == 20_000
    assert items[0].position == 1


def test_parse_traffic_supports_suffixes_and_empty_values() -> None:
    """Approximate traffic labels support common magnitude suffixes."""
    assert parse_traffic("1.5M+") == 1_500_000
    assert parse_traffic("12,300") == 12_300
    assert parse_traffic("") is None


def test_reddit_items_are_marked_as_community_signal() -> None:
    """Reddit is represented as a separate community signal."""
    assert RedditPopularSource.key == "reddit"
    assert RedditPopularSource.label == "Reddit"
    assert RedditPopularSource.ttl_seconds != 0


def test_parse_reddit_rss_does_not_invent_a_score() -> None:
    """RSS post titles and links normalize without fabricating engagement counts."""
    rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel><item>
      <title>Popular community topic</title>
      <link>https://www.reddit.com/r/example/comments/1</link>
      <description><![CDATA[<p>A <b>community</b> discussion</p>]]></description>
    </item></channel></rss>"""

    items = parse_reddit_feed(rss, country_code="gb")

    assert len(items) == 1
    assert items[0].country_code == "GB"
    assert items[0].metric == "محبوبیت جامعه"
    assert items[0].metric_value is None
    assert items[0].summary == "A community discussion"
