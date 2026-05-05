"""Run the regime engine over a time series of signal vectors."""

from __future__ import annotations

from regimeos.models.regime import RegimeState, SignalVector, TransitionRecord
from regimeos.state.classifier import classify_regime


def run_regime_engine(
    signals: list[SignalVector],
) -> tuple[list[RegimeState], list[TransitionRecord]]:
    states: list[RegimeState] = []
    transitions: list[TransitionRecord] = []
    prev: RegimeState | None = None

    for sig in signals:
        state = classify_regime(sig, prev)
        states.append(state)

        if state.transition_detected and prev is not None:
            transitions.append(TransitionRecord(
                date=state.date,
                from_regime=prev.label,
                to_regime=state.label,
                confidence=state.confidence,
                key_signals=[str(d["signal"]) for d in state.drivers[:2]],
            ))

        prev = state

    return states, transitions
