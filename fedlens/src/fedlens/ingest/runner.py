"""Orchestrate document ingestion: discover → fetch → parse → chunk → parquet."""

from __future__ import annotations

from datetime import datetime
from rich.console import Console

console = Console()


def run_ingest(
    doc_type: str = "all",
    start_year: int = 2010,
    end_year: int | None = None,
    refresh: bool = False,
) -> None:
    """Run the full ingestion pipeline."""
    from fedlens.ingest.fed_statements import StatementScraper
    from fedlens.ingest.parser import parse_document
    from fedlens.ingest.chunker import chunk_document
    from fedlens.ingest.registry import DocType
    from fedlens.storage.parquet_store import write_bronze_html, write_bronze_metadata
    from fedlens.storage.parquet_store import write_silver
    import polars as pl

    if end_year is None:
        end_year = datetime.now().year

    scrapers = {}
    if doc_type in ("all", "statement"):
        scrapers["statement"] = StatementScraper()

    # Phase 1: Discover and fetch
    for dtype, scraper in scrapers.items():
        console.print(f"\n[bold cyan]Ingesting {dtype}s ({start_year}-{end_year})...[/bold cyan]")

        docs = scraper.discover(start_year, end_year)
        console.print(f"  Discovered [yellow]{len(docs)}[/yellow] documents")

        all_chunks = []
        all_metadata = []

        for meta in docs:
            # Check if already in bronze
            from fedlens.storage.parquet_store import read_bronze_html

            if not refresh and read_bronze_html(meta.doc_id, dtype) is not None:
                console.print(f"  [dim]Skipping {meta.doc_id} (already exists)[/dim]")
                # Still parse for silver layer
                html = read_bronze_html(meta.doc_id, dtype)
            else:
                html = scraper.fetch_raw(meta)
                if html is None:
                    console.print(f"  [red]Failed to fetch {meta.doc_id}[/red]")
                    continue
                write_bronze_html(meta.doc_id, dtype, html)
                write_bronze_metadata(meta.doc_id, dtype, meta.to_dict())
                console.print(f"  [green]Fetched {meta.doc_id}[/green]")

            # Parse and chunk
            sections = parse_document(html, meta.doc_type.value)
            chunks = chunk_document(meta, sections)
            all_chunks.extend(chunks)
            all_metadata.append(meta.to_dict() | {
                "num_sections": len(sections),
                "num_chunks": len(chunks),
                "total_tokens": sum(c.token_count for c in chunks),
            })

        # Write silver layer
        if all_chunks:
            chunks_df = pl.DataFrame([
                {
                    "chunk_id": c.chunk_id,
                    "doc_id": c.doc_id,
                    "doc_type": c.doc_type,
                    "date": c.date,
                    "speaker": c.speaker,
                    "section_heading": c.section_heading,
                    "chunk_index": c.chunk_index,
                    "text": c.text,
                    "token_count": c.token_count,
                }
                for c in all_chunks
            ])
            write_silver(chunks_df, dtype, sub="parsed")
            console.print(f"  Silver: [yellow]{len(chunks_df)}[/yellow] chunks written")

        if all_metadata:
            meta_df = pl.DataFrame(all_metadata)
            write_silver(meta_df, dtype, sub="metadata")
            console.print(f"  Metadata: [yellow]{len(meta_df)}[/yellow] documents cataloged")

    console.print("\n[bold green]Ingestion complete.[/bold green]")
