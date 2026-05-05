"""RegimeOS CLI — regime detection and decision support from the terminal."""

from __future__ import annotations

import typer

from regimeos import __version__

app = typer.Typer(name="regimeos", help="Macro regime detection and decision-support orchestration")


@app.command()
def refresh() -> None:
    """Run the regime engine over sample signals and display current state."""
    from regimeos.signals.sample import get_sample_signals
    from regimeos.state.engine import run_regime_engine

    signals = get_sample_signals()
    states, transitions = run_regime_engine(signals)
    current = states[-1]

    typer.echo(f"\n=== RegimeOS — Regime State ===\n")
    typer.echo(f"  As of:       {current.date}")
    typer.echo(f"  Regime:      {current.label.value.upper()}")
    typer.echo(f"  Confidence:  {current.confidence:.0%}")
    if current.transition_detected:
        typer.echo(f"  *** TRANSITION from {current.previous_label.value} ***")
    typer.echo(f"\n  Regime Probabilities:")
    for regime, prob in sorted(current.probabilities.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(prob * 20)
        typer.echo(f"    {regime:<15} {prob:>6.1%}  {bar}")
    typer.echo(f"\n  Key Drivers:")
    for d in current.drivers[:4]:
        typer.echo(f"    {d['signal']:<30} {d['observed']:>+6.2f}  (prototype: {d['prototype']:>+5.1f})")
    typer.echo(f"\n  Transitions detected: {len(transitions)}")


@app.command(name="score-state")
def score_state(
    growth_z: float = typer.Option(0.0), inflation_z: float = typer.Option(0.0),
    financial_conditions_z: float = typer.Option(0.0), labor_z: float = typer.Option(0.0),
    vol_z: float = typer.Option(0.0), yield_curve_z: float = typer.Option(0.0),
    policy_sentiment: float = typer.Option(0.0),
) -> None:
    """Classify an ad-hoc signal vector."""
    from regimeos.models.regime import SignalVector
    from regimeos.state.classifier import classify_regime
    from datetime import date

    sig = SignalVector(
        date=str(date.today()),
        growth_z=growth_z, inflation_z=inflation_z,
        financial_conditions_z=financial_conditions_z, labor_z=labor_z,
        vol_z=vol_z, yield_curve_z=yield_curve_z, policy_sentiment=policy_sentiment,
    )
    state = classify_regime(sig)
    typer.echo(f"\nRegime: {state.label.value.upper()}  (confidence: {state.confidence:.0%})")
    for k, v in sorted(state.probabilities.items(), key=lambda x: x[1], reverse=True):
        typer.echo(f"  {k:<20} {v:.1%}")


@app.command()
def explain(question: str = typer.Argument("What regime are we in and what should we watch?")) -> None:
    """Generate a narrative regime briefing."""
    from regimeos.signals.sample import get_sample_signals
    from regimeos.state.engine import run_regime_engine
    from regimeos.agents.explainer import explain_state

    signals = get_sample_signals()
    states, _ = run_regime_engine(signals)
    briefing = explain_state(states[-1], question)
    typer.echo(f"\n{briefing}")


@app.command(name="publish-note")
def publish_note(output: str = typer.Option("regime_note.md", help="Output file")) -> None:
    """Export a regime briefing and recommendation as a Markdown note."""
    from pathlib import Path
    from regimeos.signals.sample import get_sample_signals
    from regimeos.state.engine import run_regime_engine
    from regimeos.agents.recommender import generate_recommendation
    from regimeos.agents.explainer import _fallback_explanation

    signals = get_sample_signals()
    states, _ = run_regime_engine(signals)
    current = states[-1]
    rec = generate_recommendation(current)
    briefing = _fallback_explanation(current)

    content = f"""# RegimeOS Note — {current.date}

## Current Regime: {current.label.value.upper()}

Confidence: {current.confidence:.0%}

{briefing}

## Recommendation

{rec.rationale}

### Actions
{chr(10).join(f"- {a.value}" for a in rec.actions)}

### Watchlist
{chr(10).join(f"- {w}" for w in rec.watchlist)}

### Scenario Priorities
{chr(10).join(f"- {s}" for s in rec.scenario_priorities)}

---
*Approval status: {rec.approval_status} — human review required before execution.*
"""
    Path(output).write_text(content, encoding="utf-8")
    typer.echo(f"Note written to {output}")


@app.command()
def serve(port: int = typer.Option(8003), reload: bool = typer.Option(False)) -> None:
    """Start the RegimeOS API server."""
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=reload)


@app.command()
def version() -> None:
    typer.echo(f"RegimeOS v{__version__}")


if __name__ == "__main__":
    app()
