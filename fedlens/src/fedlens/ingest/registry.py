"""Document type catalog and metadata for FedLens."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class DocType(str, Enum):
    """Types of Federal Reserve communications."""

    STATEMENT = "statement"
    MINUTES = "minutes"
    SPEECH = "speech"
    PRESS_CONFERENCE = "pressconf"


@dataclass(frozen=True)
class DocumentMeta:
    """Metadata for a single Fed communication document."""

    doc_id: str  # e.g. "statement_2024-01-31"
    doc_type: DocType
    date: date
    title: str
    url: str
    speaker: str | None = None  # for speeches
    meeting_date: date | None = None  # for statements/minutes

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "doc_type": self.doc_type.value,
            "date": self.date.isoformat(),
            "title": self.title,
            "url": self.url,
            "speaker": self.speaker,
            "meeting_date": self.meeting_date.isoformat() if self.meeting_date else None,
        }


@dataclass(frozen=True)
class Section:
    """A parsed section from a Fed document."""

    heading: str
    text: str
    char_offset: int


@dataclass(frozen=True)
class Chunk:
    """A semantic chunk from a parsed document, ready for embedding."""

    chunk_id: str
    doc_id: str
    doc_type: str
    date: date
    speaker: str | None
    section_heading: str
    chunk_index: int
    text: str
    token_count: int


# --- Document URL patterns ---

FED_BASE = "https://www.federalreserve.gov"

STATEMENT_CALENDAR_URL = f"{FED_BASE}/monetarypolicy/fomccalendars.htm"
STATEMENT_ARCHIVE_URL = f"{FED_BASE}/monetarypolicy/fomc_historical_year.htm"
MINUTES_ARCHIVE_URL = f"{FED_BASE}/monetarypolicy/fomc_historical_year.htm"
SPEECHES_URL = f"{FED_BASE}/newsevents/speeches.htm"
PRESSCONF_URL = f"{FED_BASE}/monetarypolicy/fomcpresconf.htm"
