"""HTML → structured text parser for Fed documents."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from fedlens.ingest.registry import Section


def parse_document(html: str, doc_type: str) -> list[Section]:
    """Parse raw HTML into structured sections.

    Returns a list of Section objects with heading, text, and char_offset.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    if doc_type == "statement":
        return _parse_statement(soup)
    elif doc_type == "minutes":
        return _parse_minutes(soup)
    elif doc_type == "speech":
        return _parse_speech(soup)
    elif doc_type == "pressconf":
        return _parse_pressconf(soup)
    else:
        return _parse_generic(soup)


def _parse_statement(soup: BeautifulSoup) -> list[Section]:
    """Parse FOMC statement — typically a single section."""
    # Try to find the main content area
    content = (
        soup.find("div", class_="col-xs-12 col-sm-8 col-md-8")
        or soup.find("div", id="article")
        or soup.find("article")
        or soup.find("div", class_="row")
    )

    if content is None:
        content = soup.body or soup

    # Extract paragraphs
    paragraphs = []
    for p in content.find_all("p"):
        text = _clean_text(p.get_text())
        if text and len(text) > 20:  # Skip tiny fragments
            paragraphs.append(text)

    if not paragraphs:
        # Fallback: get all text from content
        text = _clean_text(content.get_text())
        if text:
            paragraphs = [text]

    # Group into logical sections
    sections = []
    if paragraphs:
        # First section: the main policy statement
        full_text = "\n\n".join(paragraphs)
        sections.append(Section(
            heading="FOMC Statement",
            text=full_text,
            char_offset=0,
        ))

        # Try to identify vote section (last paragraph often contains vote info)
        for p in paragraphs:
            if "voting for" in p.lower() or "voted to" in p.lower():
                sections.append(Section(
                    heading="Voting",
                    text=p,
                    char_offset=full_text.index(p) if p in full_text else 0,
                ))
                break

    return sections if sections else [Section("Full Text", _clean_text(content.get_text()), 0)]


def _parse_minutes(soup: BeautifulSoup) -> list[Section]:
    """Parse FOMC minutes — multiple headed sections."""
    sections = []
    current_heading = "Introduction"
    current_text: list[str] = []
    offset = 0

    content = soup.find("div", class_="col-xs-12 col-sm-8 col-md-8") or soup.body or soup

    for elem in content.find_all(["h2", "h3", "h4", "h5", "p", "strong"]):
        if elem.name in ("h2", "h3", "h4", "h5") or (
            elem.name == "strong" and elem.parent.name == "p" and len(elem.get_text(strip=True)) > 5
        ):
            # Save previous section
            if current_text:
                text = "\n\n".join(current_text)
                sections.append(Section(heading=current_heading, text=text, char_offset=offset))
                offset += len(text)
            current_heading = _clean_text(elem.get_text())
            current_text = []
        elif elem.name == "p":
            text = _clean_text(elem.get_text())
            if text and len(text) > 20:
                current_text.append(text)

    # Final section
    if current_text:
        text = "\n\n".join(current_text)
        sections.append(Section(heading=current_heading, text=text, char_offset=offset))

    return sections if sections else [Section("Full Text", _clean_text(content.get_text()), 0)]


def _parse_speech(soup: BeautifulSoup) -> list[Section]:
    """Parse a Fed speech."""
    return _parse_generic(soup)


def _parse_pressconf(soup: BeautifulSoup) -> list[Section]:
    """Parse press conference transcript."""
    return _parse_generic(soup)


def _parse_generic(soup: BeautifulSoup) -> list[Section]:
    """Generic fallback parser."""
    content = soup.body or soup
    text = _clean_text(content.get_text())
    if text:
        return [Section(heading="Full Text", text=text, char_offset=0)]
    return []


def _clean_text(text: str) -> str:
    """Clean up extracted text."""
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text
