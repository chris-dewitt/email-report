"""BalanceLab CLI — balance-sheet risk analytics from the command line."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from balancelab import __version__

app = typer.Typer(name="balancelab", help="ALM, NII, EVE, and scenario analytics platform")


@app.command()
def init() -> None:
    """Initialize data directories and DuckDB."""
    from balancelab.storage.paths import ensure_data_dirs
    from balancelab.storage.duckdb_store import get_connection, register_views

    ensure_data_dirs()
    conn = get_connection()
    register_views(conn)
    typer.echo("BalanceLab initialized — data directories and DuckDB ready.")


@app.command()
def load(path: Path = typer.Argument(..., help="Path to balance-sheet JSON file")) -> None:
    """Load a balance sheet from a JSON file."""
    from balancelab.scenarios.loader import load_balance_sheet

    bs = load_balance_sheet(path)
    typer.echo(f"Loaded: {bs.name} ({bs.as_of_date})")
    typer.echo(f"  Positions: {len(bs.positions)}")
    typer.echo(f"  Total assets:      ${bs.total_assets:>15,.0f}")
    typer.echo(f"  Total liabilities: ${bs.total_liabilities:>15,.0f}")
    typer.echo(f"  Equity:            ${bs.equity:>15,.0f}")


@app.command(name="map-products")
def map_products(path: Path = typer.Argument(..., help="Balance-sheet JSON")) -> None:
    """Show product mapping and repricing profile for a balance sheet."""
    from balancelab.scenarios.loader import load_balance_sheet

    bs = load_balance_sheet(path)
    typer.echo(f"\n{'ID':<6} {'Name':<30} {'Class':<22} {'Bucket':<12} {'Balance':>15} {'Rate':>8}")
    typer.echo("-" * 100)
    for p in bs.positions:
        side = "A" if p.is_asset else "L"
        typer.echo(
            f"{p.id:<6} {p.name[:29]:<30} {p.asset_class.value:<22} "
            f"{p.repricing_bucket.value:<12} ${p.balance:>14,.0f} {p.rate:>7.2%} [{side}]"
        )


@app.command()
def shock(
    path: Path = typer.Argument(..., help="Balance-sheet JSON"),
    scenario: str = typer.Option("up_200", help="Scenario ID to run"),
) -> None:
    """Run a rate scenario and display NII/EVE/gap results."""
    from balancelab.scenarios.loader import load_balance_sheet
    from balancelab.scenarios.catalog import ScenarioCatalog
    from balancelab.core.engine import run_scenario

    bs = load_balance_sheet(path)
    catalog = ScenarioCatalog()
    scen = catalog.get(scenario)
    if scen is None:
        typer.echo(f"Unknown scenario: {scenario}. Available: {catalog.ids}", err=True)
        raise typer.Exit(1)

    result = run_scenario(bs, scen)
    nii = result.nii
    eve = result.eve
    liq = result.liquidity

    typer.echo(f"\n=== {result.scenario_name} ===\n")
    typer.echo(f"NII Impact ({nii.horizon_months}mo horizon):")
    typer.echo(f"  Base NII:    ${nii.base_nii:>15,.0f}")
    typer.echo(f"  Shocked NII: ${nii.shocked_nii:>15,.0f}")
    typer.echo(f"  Delta NII:   ${nii.delta_nii:>15,.0f}  ({nii.delta_nii_pct:+.1f}%)")

    typer.echo(f"\nEVE Impact:")
    typer.echo(f"  Base EVE:    ${eve.base_eve:>15,.0f}")
    typer.echo(f"  Shocked EVE: ${eve.shocked_eve:>15,.0f}")
    typer.echo(f"  Delta EVE:   ${eve.delta_eve:>15,.0f}  ({eve.delta_eve_pct:+.1f}%)")
    typer.echo(f"  Duration gap: {eve.duration_gap:.2f}y  (A: {eve.asset_duration:.2f}y, L: {eve.liability_duration:.2f}y)")

    typer.echo(f"\nRepricing Gap Table:")
    typer.echo(f"  {'Bucket':<15} {'RSA':>15} {'RSL':>15} {'Gap':>15} {'Cumul':>15}")
    typer.echo("  " + "-" * 78)
    for row in liq.gap_table:
        typer.echo(
            f"  {row.bucket:<15} ${row.rsa:>14,.0f} ${row.rsl:>14,.0f} "
            f"${row.gap:>14,.0f} ${row.cumulative_gap:>14,.0f}"
        )

    if nii.top_drivers:
        typer.echo(f"\nTop NII Drivers:")
        for d in nii.top_drivers[:5]:
            typer.echo(f"  {d['name']}: ${d['delta_income']:>12,.0f} ({d['side']})")


@app.command(name="export-pack")
def export_pack(
    path: Path = typer.Argument(..., help="Balance-sheet JSON"),
    output: Path = typer.Option(Path("./balancelab_export.json"), help="Output file"),
) -> None:
    """Run all standard scenarios and export results as JSON."""
    from balancelab.scenarios.loader import load_balance_sheet
    from balancelab.core.engine import run_all_scenarios
    from balancelab.models.scenarios import STANDARD_SCENARIOS

    bs = load_balance_sheet(path)
    results = run_all_scenarios(bs, STANDARD_SCENARIOS)

    export = {
        "balance_sheet": bs.model_dump(),
        "results": [r.model_dump() for r in results],
    }
    output.write_text(json.dumps(export, indent=2, default=str), encoding="utf-8")
    typer.echo(f"Exported {len(results)} scenarios to {output}")


@app.command()
def serve(
    port: int = typer.Option(8001, help="Port"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
) -> None:
    """Start the BalanceLab API server."""
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=reload)


@app.command()
def version() -> None:
    """Show version."""
    typer.echo(f"BalanceLab v{__version__}")


if __name__ == "__main__":
    app()
