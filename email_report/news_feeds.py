"""Parse RSS feeds for Fed publications, economic analysis, and AI news."""

import logging
from datetime import datetime, timedelta, timezone

import feedparser

logger = logging.getLogger(__name__)


def _recent_entries(feed_url: str, hours: int = 48, max_items: int = 5) -> list[dict]:
    """Parse an RSS feed and return recent entries."""
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo and not feed.entries:
            logger.warning("Failed to parse feed %s: %s", feed_url, feed.bozo_exception)
            return []

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        results = []

        for entry in feed.entries:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if published:
                pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                if pub_dt < cutoff:
                    continue

            title = entry.get("title", "Untitled")
            link = entry.get("link", "")
            summary = entry.get("summary", "")
            # Truncate long summaries
            if len(summary) > 300:
                summary = summary[:297] + "..."

            results.append({
                "title": title,
                "link": link,
                "summary": summary,
                "published": published,
            })

            if len(results) >= max_items:
                break

        return results

    except Exception:
        logger.exception("Error fetching feed %s", feed_url)
        return []


def fetch_fed_publications(feed_urls: list[str], max_items: int = 5) -> list[dict]:
    """Fetch recent Federal Reserve publications from RSS feeds."""
    all_items = []
    for url in feed_urls:
        all_items.extend(_recent_entries(url, hours=48, max_items=max_items))
    return all_items[:max_items]


def fetch_econ_analysis(feed_urls: list[str], max_items: int = 5) -> list[dict]:
    """Fetch recent economic analysis from NBER, Brookings, etc."""
    all_items = []
    for url in feed_urls:
        items = _recent_entries(url, hours=72, max_items=max_items)
        for item in items:
            item["source"] = _source_name(url)
        all_items.extend(items)
    return all_items[:max_items]


def fetch_ai_news(feed_urls: list[str], max_items: int = 8) -> list[dict]:
    """Fetch recent AI news and research from RSS feeds."""
    all_items = []
    for url in feed_urls:
        items = _recent_entries(url, hours=48, max_items=max_items)
        for item in items:
            item["source"] = _source_name(url)
        all_items.extend(items)
    return all_items[:max_items]


def _source_name(url: str) -> str:
    """Extract a readable source name from a feed URL."""
    if "arxiv" in url:
        return "arXiv"
    if "federalreserve" in url:
        return "Federal Reserve"
    if "nber" in url:
        return "NBER"
    if "brookings" in url:
        return "Brookings"
    if "arstechnica" in url:
        return "Ars Technica"
    return url.split("/")[2] if "/" in url else url
