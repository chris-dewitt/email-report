"""FedLens CLI — Typer application."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(
    name="fedlens",
    help="FedLens — Fed Communication Intelligence Engine",
    add_completion=False,
)
console = Console()


@app.command()
def init():
    """Create data directories and initialize DuckDB."""
    from fedlens.storage.paths import ensure_dirs, duckdb_path

    ensure_dirs()
    # Touch DuckDB to create it
    import duckdb

    conn = duckdb.connect(str(duckdb_path()))
    conn.close()
    console.print("[green]FedLens initialized.[/green] Data directories created.")


@app.command()
def ingest(
    doc_type: str = typer.Option("all", help="Document type: statement, minutes, speech, pressconf, or all"),
    start_year: int = typer.Option(2010, help="Start year for ingestion"),
    end_year: Optional[int] = typer.Option(None, help="End year (default: current year)"),
    refresh: bool = typer.Option(False, help="Only re-scrape last 90 days"),
):
    """Scrape and parse Fed documents into bronze/silver layers."""
    from fedlens.ingest.runner import run_ingest

    run_ingest(doc_type=doc_type, start_year=start_year, end_year=end_year, refresh=refresh)


@app.command()
def embed(
    rebuild: bool = typer.Option(False, help="Re-embed everything from scratch"),
):
    """Generate embeddings and build FAISS index."""
    from fedlens.models.embedder import build_embeddings

    build_embeddings(rebuild=rebuild)


@app.command()
def analyze():
    """Run NLP feature pipeline: sentiment, uncertainty, drift."""
    from fedlens.models.feature_builder import build_all_features

    build_all_features()


@app.command(name="event-study")
def event_study(
    series: str = typer.Option("DGS10", help="Market series to study"),
    doc_type: str = typer.Option("statement", help="Document type to analyze"),
    all_series: bool = typer.Option(False, "--all", help="Run against all market series"),
):
    """Run event studies — market reactions to Fed communications."""
    from fedlens.eventstudy.engine import run_event_studies

    run_event_studies(series_id=series, doc_type=doc_type, run_all=all_series)


@app.command()
def brief(
    question: Optional[str] = typer.Option(None, help="Question to answer"),
    doc_id: Optional[str] = typer.Option(None, help="Specific document to analyze"),
):
    """Generate a policy briefing using the local LLM copilot."""
    from fedlens.agents.briefing_agent import run_briefing

    result = run_briefing(question=question, doc_id=doc_id)
    console.print(result)


@app.command()
def serve(
    port: int = typer.Option(8001, help="Port to serve on"),
    reload: bool = typer.Option(True, help="Enable auto-reload"),
):
    """Launch the FedLens API server."""
    import sys
    import uvicorn
    from pathlib import Path

    # Ensure FedLens's src/ is first on sys.path so api.main resolves here, not Atlas
    src_dir = str(Path(__file__).resolve().parent.parent.parent)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        reload_dirs=[src_dir],
    )


@app.command()
def status():
    """Show data freshness, document counts, and index stats."""
    from fedlens.storage.paths import (
        bronze_dir,
        silver_dir,
        gold_dir,
        vector_dir,
    )

    console.print("\n[bold cyan]FedLens Status[/bold cyan]\n")

    # Count bronze documents
    for dtype in ("statements", "minutes", "speeches", "pressconf"):
        d = bronze_dir(dtype)
        html_count = len(list(d.glob("*.html"))) if d.exists() else 0
        console.print(f"  Bronze/{dtype}: [yellow]{html_count}[/yellow] documents")

    # Silver chunks
    parsed_dir = silver_dir("parsed")
    if parsed_dir.exists():
        import polars as pl

        total_chunks = 0
        for pq in parsed_dir.glob("*.parquet"):
            df = pl.read_parquet(pq)
            total_chunks += len(df)
        console.print(f"  Silver/parsed: [yellow]{total_chunks}[/yellow] chunks")
    else:
        console.print("  Silver/parsed: [dim]not built[/dim]")

    # FAISS index
    faiss_path = vector_dir() / "faiss.index"
    if faiss_path.exists():
        size_mb = faiss_path.stat().st_size / (1024 * 1024)
        console.print(f"  Vector index: [yellow]{size_mb:.1f} MB[/yellow]")
    else:
        console.print("  Vector index: [dim]not built[/dim]")

    # Gold layers
    for sub in ("sentiment", "event_study", "topics", "drift"):
        d = gold_dir(sub)
        pq_count = len(list(d.glob("*.parquet"))) if d.exists() else 0
        console.print(f"  Gold/{sub}: [yellow]{pq_count}[/yellow] parquets")

    console.print()


if __name__ == "__main__":
    app()
