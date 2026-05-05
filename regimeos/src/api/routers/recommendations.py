from __future__ import annotations

from fastapi import APIRouter

from regimeos.models.recommendation import Recommendation
from regimeos.agents.recommender import generate_recommendation
from regimeos.agents.explainer import explain_state
from regimeos.state.engine import run_regime_engine
from regimeos.signals.sample import get_sample_signals

router = APIRouter()


@router.get("", response_model=Recommendation)
def get_recommendation() -> Recommendation:
    signals = get_sample_signals()
    states, _ = run_regime_engine(signals)
    return generate_recommendation(states[-1])


@router.get("/explain")
def explain(question: str | None = None) -> dict[str, str]:
    signals = get_sample_signals()
    states, _ = run_regime_engine(signals)
    briefing = explain_state(states[-1], question)
    return {"regime": states[-1].label.value, "briefing": briefing}
