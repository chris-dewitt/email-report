"""Atlas CLI — command-line interface for the macro intelligence platform."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="atlas",
    help="Atlas — Macro Intelligence Platform",
    add_completion=False,
)
console = Console()


@app.command()
def init() -> None:
    """Initialize data directories and empty DuckDB."""
    from atlas.storage.paths import ensure_dirs, duckdb_path
    from atlas.storage.duckdb_store import DuckDBStore

    ensure_dirs()
    console.print("[green][OK] Data directories created.[/green]")

    db = DuckDBStore()
    db.close()
    console.print(f"[green][OK] DuckDB initialized at {duckdb_path()}[/green]")

    console.print("\n[bold]Atlas initialized. Run 'atlas pull' to fetch data.[/bold]")


@app.command()
def pull(
    source: str = typer.Option(None, "--source", "-s", help="Source filter: fred, yfinance"),
    series: str = typer.Option(None, "--series", help="Pull a specific series ID"),
) -> None:
    """Pull raw data from all sources into the bronze layer."""
    from atlas.ingest.runner import run_ingest, print_ingest_report
    from atlas.ingest.registry import Source
    from atlas.storage.paths import ensure_dirs

    ensure_dirs()

    source_enum = None
    if source:
        try:
            source_enum = Source(source)
        except ValueError:
            console.print(f"[red]Unknown source: {source}. Use 'fred' or 'yfinance'.[/red]")
            raise typer.Exit(code=1)

    console.print("[bold]Pulling macro data...[/bold]\n")
    results = run_ingest(source_filter=source_enum, series_filter=series)
    print_ingest_report(results)


@app.command(name="build-features")
def build_features(
    theme: str = typer.Option(None, "--theme", "-t", help="Theme filter: inflation, labor, rates, fincond, growth, fx_market"),
) -> None:
    """Build silver and gold feature layers from bronze data."""
    from atlas.features.builder import run_feature_pipeline
    from atlas.storage.duckdb_store import DuckDBStore

    console.print("[bold]Building features...[/bold]\n")
    stats = run_feature_pipeline(theme_filter=theme)

    for layer, count in stats.items():
        console.print(f"  [cyan]{layer}[/cyan]: {count} rows")

    # Register in DuckDB
    db = DuckDBStore()
    view_stats = db.register_views()
    db.close()
    console.print(f"\n[green][OK] {len(view_stats)} DuckDB views registered.[/green]")


@app.command()
def snapshot() -> None:
    """Compute and display the current macro regime classification."""
    from atlas.features.regime import compute_regime_snapshot

    result = compute_regime_snapshot()
    if result is None:
        console.print("[red]No feature data available. Run 'atlas build-features' first.[/red]")
        raise typer.Exit(code=1)

    console.print(f"\n[bold]Regime: {result['regime'].upper()}[/bold]")
    console.print(f"Confidence: {result['confidence']:.0%}")
    console.print(f"As of: {result['as_of']}")
    console.print("\nTop drivers:")
    for driver in result["drivers"]:
        console.print(f"  -{driver}")


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p"),
    reload: bool = typer.Option(False, "--reload"),
) -> None:
    """Launch the FastAPI server."""
    import uvicorn

    console.print(f"[bold]Starting Atlas API on port {port}...[/bold]")
    uvicorn.run(
        "api.main:create_app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        factory=True,
    )


@app.command()
def status() -> None:
    """Show data freshness, series health, and DuckDB stats."""
    from atlas.storage.paths import bronze_dir, duckdb_path
    from atlas.storage.duckdb_store import DuckDBStore
    from atlas.ingest.registry import SERIES_CATALOG

    table = Table(title="Atlas Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    # Series catalog
    table.add_row("Catalog series", str(len(SERIES_CATALOG)))

    # Bronze files
    bronze_files = list(bronze_dir().rglob("*.parquet"))
    table.add_row("Bronze parquets", str(len(bronze_files)))

    # DuckDB
    db_path = duckdb_path()
    if db_path.exists():
        db = DuckDBStore()
        try:
            stats = db.table_stats()
            table.add_row("DuckDB views", str(len(stats)))
            for view_name, count in stats.items():
                table.add_row(f"  > {view_name}", f"{count:,} rows")
        finally:
            db.close()
    else:
        table.add_row("DuckDB", "not initialized")

    console.print(table)


@app.command()
def copilot(
    question: str = typer.Option(None, "--question", "-q", help="Question for the macro copilot"),
) -> None:
    """Run a macro briefing via Ollama."""
    from atlas.copilot.briefing import generate_briefing

    console.print("[bold]Generating macro briefing...[/bold]\n")
    try:
        result = generate_briefing(question=question)
        console.print(result["summary"])
        if result.get("citations"):
            console.print("\n[dim]Citations:[/dim]")
            for c in result["citations"]:
                console.print(f"  [{c}]")
    except Exception as e:
        console.print(f"[red]Copilot error: {e}[/red]")
        console.print("[dim]Is Ollama running? Check: curl http://localhost:11434/api/tags[/dim]")


@app.command(name="export-report")
def export_report(
    fmt: str = typer.Option("csv", "--format", "-f", help="Export format: csv, json"),
    output: str = typer.Option("./data/gold/exports", "--output", "-o"),
) -> None:
    """Export gold-layer data as a report bundle."""
    from atlas.storage.paths import gold_dir
    import polars as pl

    out_path = Path(output)
    out_path.mkdir(parents=True, exist_ok=True)

    feature_dir = gold_dir("features")
    files = list(feature_dir.glob("*.parquet"))

    if not files:
        console.print("[red]No gold features to export. Run 'atlas build-features' first.[/red]")
        raise typer.Exit(code=1)

    for f in files:
        df = pl.read_parquet(f)
        name = f.stem
        if fmt == "csv":
            df.write_csv(out_path / f"{name}.csv")
        elif fmt == "json":
            df.write_json(out_path / f"{name}.json")
        console.print(f"  [green][OK][/green] {name}.{fmt}")

    console.print(f"\n[bold]Exported {len(files)} files to {out_path}[/bold]")


if __name__ == "__main__":
    app()
