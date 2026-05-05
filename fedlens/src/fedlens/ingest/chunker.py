"""Semantic chunking for Fed documents."""

from __future__ import annotations

import hashlib
from typing import Sequence

from fedlens.config import get_settings
from fedlens.ingest.registry import Chunk, DocumentMeta, Section


def _simple_token_count(text: str) -> int:
    """Approximate token count using whitespace splitting.

    A rough 1.3x multiplier accounts for subword tokenization.
    """
    return int(len(text.split()) * 1.3)


def _generate_chunk_id(doc_id: str, section: str, offset: int) -> str:
    """Generate a deterministic chunk ID."""
    raw = f"{doc_id}::{section}::{offset}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def chunk_section(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[tuple[str, int]]:
    """Split text into overlapping chunks by approximate token count.

    Returns list of (chunk_text, word_offset) tuples.
    """
    words = text.split()
    if not words:
        return []

    # Convert token counts to approximate word counts
    word_chunk = int(chunk_size / 1.3)
    word_overlap = int(overlap / 1.3)

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + word_chunk, len(words))
        chunk_text = " ".join(words[start:end])
        chunks.append((chunk_text, start))

        if end >= len(words):
            break
        start = end - word_overlap

    return chunks


def chunk_document(
    meta: DocumentMeta,
    sections: Sequence[Section],
) -> list[Chunk]:
    """Split parsed sections into semantic chunks.

    Each chunk gets a deterministic chunk_id based on doc_id + section + offset.
    """
    settings = get_settings().ingest
    chunk_size = settings.chunk_size_tokens
    chunk_overlap = settings.chunk_overlap_tokens

    all_chunks: list[Chunk] = []
    chunk_index = 0

    for section in sections:
        text_chunks = chunk_section(section.text, chunk_size, chunk_overlap)

        for chunk_text, word_offset in text_chunks:
            chunk_id = _generate_chunk_id(meta.doc_id, section.heading, word_offset)
            token_count = _simple_token_count(chunk_text)

            all_chunks.append(Chunk(
                chunk_id=chunk_id,
                doc_id=meta.doc_id,
                doc_type=meta.doc_type.value,
                date=meta.date,
                speaker=meta.speaker,
                section_heading=section.heading,
                chunk_index=chunk_index,
                text=chunk_text,
                token_count=token_count,
            ))
            chunk_index += 1

    return all_chunks
