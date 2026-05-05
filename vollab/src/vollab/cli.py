"""VolLab CLI — derivatives analytics from the command line."""

from __future__ import annotations

import typer

from vollab import __version__
from vollab.models.option import OptionContract, OptionType

app = typer.Typer(name="vollab", help="Derivatives pricing, Greeks, and vol surface lab")


def _default_contract(
    spot: float, strike: float, expiry: float, vol: float,
    rate: float, put: bool,
) -> OptionContract:
    return OptionContract(
        spot=spot, strike=strike, expiry=expiry, vol=vol, rate=rate,
        option_type=OptionType.PUT if put else OptionType.CALL,
    )


@app.command()
def price(
    spot: float = typer.Option(100.0, help="Underlying price"),
    strike: float = typer.Option(100.0, help="Strike price"),
    expiry: float = typer.Option(1.0, help="Years to expiration"),
    vol: float = typer.Option(0.20, help="Annualized vol"),
    rate: float = typer.Option(0.05, help="Risk-free rate"),
    put: bool = typer.Option(False, help="Price a put instead of call"),
) -> None:
    """Price an option using Black-Scholes and Monte Carlo."""
    from vollab.pricing import price_bs, price_mc

    c = _default_contract(spot, strike, expiry, vol, rate, put)
    bs = price_bs(c)
    mc = price_mc(c)

    otype = "PUT" if put else "CALL"
    typer.echo(f"\n{otype}  S={spot}  K={strike}  T={expiry}y  σ={vol:.1%}  r={rate:.2%}")
    typer.echo(f"  Black-Scholes: ${bs.price:>10.4f}")
    typer.echo(f"  Monte Carlo:   ${mc.price:>10.4f}  (SE: {mc.mc_std_error:.6f}, paths: {mc.mc_paths:,})")
    typer.echo(f"  Intrinsic:     ${bs.intrinsic:>10.4f}")
    typer.echo(f"  Time value:    ${bs.time_value:>10.4f}")


@app.command()
def greeks(
    spot: float = typer.Option(100.0), strike: float = typer.Option(100.0),
    expiry: float = typer.Option(1.0), vol: float = typer.Option(0.20),
    rate: float = typer.Option(0.05), put: bool = typer.Option(False),
) -> None:
    """Compute Greeks (analytical and finite-difference)."""
    from vollab.greeks import compute_greeks, compute_greeks_fd

    c = _default_contract(spot, strike, expiry, vol, rate, put)
    an = compute_greeks(c)
    fd = compute_greeks_fd(c)

    typer.echo(f"\n{'Greek':<10} {'Analytical':>12} {'Finite-Diff':>12}")
    typer.echo("-" * 36)
    for name in ("delta", "gamma", "theta", "vega", "rho"):
        typer.echo(f"{name:<10} {getattr(an, name):>12.6f} {getattr(fd, name):>12.6f}")


@app.command()
def surface(spot: float = typer.Option(100.0, help="Underlying price")) -> None:
    """Display a sample vol surface with skew."""
    from vollab.surface.builder import sample_skew_surface

    strikes, expiries, vols = sample_skew_surface(spot)
    header = f"{'T \\ K':>8}" + "".join(f"{K:>8.0f}" for K in strikes)
    typer.echo(f"\nVol Surface (spot={spot})")
    typer.echo(header)
    typer.echo("-" * len(header))
    for i, T in enumerate(expiries):
        row = f"{T:>8.3f}" + "".join(f"{v:>8.1%}" for v in vols[i])
        typer.echo(row)


@app.command()
def stress(
    spot: float = typer.Option(100.0), strike: float = typer.Option(100.0),
    expiry: float = typer.Option(1.0), vol: float = typer.Option(0.20),
    rate: float = typer.Option(0.05), put: bool = typer.Option(False),
) -> None:
    """Run a spot/vol stress grid and show PnL."""
    from vollab.simulation.scenario import compute_scenario_pnl

    c = _default_contract(spot, strike, expiry, vol, rate, put)
    results = compute_scenario_pnl(c)

    vol_shifts = sorted(set(r.vol_shift for r in results))
    spot_shifts = sorted(set(r.spot_shift for r in results))

    header = f"{'S\\σ':>8}" + "".join(f"{dv:>+8.1%}" for dv in vol_shifts)
    typer.echo(f"\nPnL Grid (base=${results[0].base_price:.2f})")
    typer.echo(header)
    typer.echo("-" * len(header))

    lookup = {(r.spot_shift, r.vol_shift): r.pnl for r in results}
    for ds in spot_shifts:
        row = f"{ds:>+8.0%}" + "".join(f"{lookup[(ds, dv)]:>8.2f}" for dv in vol_shifts)
        typer.echo(row)


@app.command()
def benchmark(n_paths: int = typer.Option(500_000, help="MC paths")) -> None:
    """Benchmark BS vs MC pricing speed."""
    import time
    from vollab.pricing import price_bs, price_mc

    c = _default_contract(100, 100, 1.0, 0.2, 0.05, False)

    t0 = time.perf_counter()
    for _ in range(10_000):
        price_bs(c)
    bs_time = (time.perf_counter() - t0) / 10_000

    t0 = time.perf_counter()
    price_mc(c, n_paths=n_paths)
    mc_time = time.perf_counter() - t0

    typer.echo(f"\nBS  (10k calls):  {bs_time*1e6:>8.1f} μs/call")
    typer.echo(f"MC  ({n_paths:,} paths): {mc_time*1e3:>8.1f} ms")
    typer.echo(f"Speedup: {mc_time / (bs_time * 10_000):>8.0f}x slower")


@app.command()
def serve(
    port: int = typer.Option(8002, help="Port"),
    reload: bool = typer.Option(False),
) -> None:
    """Start the VolLab API server."""
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=reload)


@app.command()
def version() -> None:
    """Show version."""
    typer.echo(f"VolLab v{__version__}")


if __name__ == "__main__":
    app()
