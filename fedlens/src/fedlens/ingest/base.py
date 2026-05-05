"""Abstract base class for Fed document scrapers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from fedlens.ingest.registry import DocumentMeta


class BaseScraper(ABC):
    """Base class for all Fed document scrapers."""

    @abstractmethod
    def discover(self, start_year: int, end_year: int) -> list[DocumentMeta]:
        """Discover available documents in the given year range.

        Returns a list of DocumentMeta with URLs ready to fetch.
        """
        ...

    @abstractmethod
    def fetch_raw(self, meta: DocumentMeta) -> str | None:
        """Fetch raw HTML for a document. Returns None on failure."""
        ...
