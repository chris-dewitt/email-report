"""FOMC Statement scraper — discovers and fetches FOMC press releases."""

from __future__ import annotations

import re
import time
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from fedlens.config import get_settings
from fedlens.ingest.base import BaseScraper
from fedlens.ingest.registry import DocType, DocumentMeta, FED_BASE


class StatementScraper(BaseScraper):
    """Scraper for FOMC monetary policy statements."""

    def __init__(self):
        self.delay = get_settings().ingest.scrape_delay_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FedLens Research Tool (academic/portfolio project)",
        })

    def discover(self, start_year: int, end_year: int) -> list[DocumentMeta]:
        """Discover FOMC statements from the Fed website."""
        docs: list[DocumentMeta] = []

        # Current calendar page (recent years)
        docs.extend(self._discover_from_calendar())

        # Historical pages
        for year in range(start_year, end_year + 1):
            docs.extend(self._discover_from_archive(year))

        # Deduplicate by doc_id
        seen = set()
        unique = []
        for d in docs:
            if d.doc_id not in seen:
                seen.add(d.doc_id)
                if d.date.year >= start_year and d.date.year <= end_year:
                    unique.append(d)

        return sorted(unique, key=lambda d: d.date)

    def _discover_from_calendar(self) -> list[DocumentMeta]:
        """Parse the main FOMC calendar page for statement links."""
        docs = []
        try:
            resp = self.session.get(
                f"{FED_BASE}/monetarypolicy/fomccalendars.htm",
                timeout=30,
            )
            resp.raise_for_status()
            time.sleep(self.delay)

            soup = BeautifulSoup(resp.text, "lxml")

            # Look for links to monetary policy press releases
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "newsevents/pressreleases/monetary" in href:
                    meta = self._parse_statement_link(href, link.get_text(strip=True))
                    if meta:
                        docs.append(meta)

        except Exception as e:
            print(f"Warning: calendar discovery failed: {e}")

        return docs

    def _discover_from_archive(self, year: int) -> list[DocumentMeta]:
        """Parse historical FOMC pages for a given year."""
        docs = []
        try:
            url = f"{FED_BASE}/monetarypolicy/fomchistorical{year}.htm"
            resp = self.session.get(url, timeout=30)
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            time.sleep(self.delay)

            soup = BeautifulSoup(resp.text, "lxml")

            for link in soup.find_all("a", href=True):
                href = link["href"]
                text = link.get_text(strip=True).lower()
                if ("statement" in text or "press release" in text) and (
                    "newsevents/pressreleases/monetary" in href
                    or "monetarypolicy/fomcpresconf" not in href
                ):
                    meta = self._parse_statement_link(href, link.get_text(strip=True))
                    if meta:
                        docs.append(meta)

        except Exception as e:
            print(f"Warning: archive discovery for {year} failed: {e}")

        return docs

    def _parse_statement_link(self, href: str, link_text: str) -> DocumentMeta | None:
        """Extract metadata from a statement link."""
        # Normalize URL
        if href.startswith("/"):
            href = f"{FED_BASE}{href}"

        # Extract date from URL pattern like monetary20240131a.htm
        date_match = re.search(r"monetary(\d{8})", href)
        if not date_match:
            return None

        date_str = date_match.group(1)
        try:
            doc_date = datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            return None

        doc_id = f"statement_{doc_date.isoformat()}"

        return DocumentMeta(
            doc_id=doc_id,
            doc_type=DocType.STATEMENT,
            date=doc_date,
            title=f"FOMC Statement — {doc_date.strftime('%B %d, %Y')}",
            url=href,
            speaker=None,
            meeting_date=doc_date,
        )

    def fetch_raw(self, meta: DocumentMeta) -> str | None:
        """Fetch the raw HTML of a statement page."""
        try:
            resp = self.session.get(meta.url, timeout=30)
            resp.raise_for_status()
            time.sleep(self.delay)
            return resp.text
        except Exception as e:
            print(f"Error fetching {meta.url}: {e}")
            return None
