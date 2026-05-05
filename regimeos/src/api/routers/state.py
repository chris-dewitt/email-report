from __future__ import annotations

from fastapi import APIRouter

from regimeos.models.regime import RegimeState, SignalVector
from regimeos.state.classifier import classify_regime
from regimeos.state.engine import run_regime_engine
from regimeos.signals.sample import get_sample_signals

router = APIRouter()


@router.get("", response_model=RegimeState)
def current_state() -> RegimeState:
    signals = get_sample_signals()
    states, _ = run_regime_engine(signals)
    return states[-1]


@router.get("/history", response_model=list[RegimeState])
def state_history() -> list[RegimeState]:
    signals = get_sample_signals()
    states, _ = run_regime_engine(signals)
    return states


@router.get("/uncertainty", response_model=dict[str, float])
def uncertainty() -> dict[str, float]:
    signals = get_sample_signals()
    states, _ = run_regime_engine(signals)
    return states[-1].probabilities


@router.post("/classify", response_model=RegimeState)
def classify(signal: SignalVector) -> RegimeState:
    return classify_regime(signal)
