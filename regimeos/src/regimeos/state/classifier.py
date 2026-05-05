"""Rule-based regime classifier with probabilistic confidence scoring.

State assignment: p(z_t = k | x_t) is computed via a softmax over
per-regime affinity scores derived from signal thresholds.

Regimes:
  Expansion:    growth↑, inflation moderate, financial conditions easy
  Overheating:  growth↑, inflation↑↑, financial conditions tightening
  Slowdown:     growth↓, inflation moderate/falling, conditions tightening
  Contraction:  growth↓↓, inflation↓, conditions tight
  Crisis:       growth↓↓, vol↑↑, conditions very tight
"""

from __future__ import annotations

import math

from regimeos.models.regime import RegimeLabel, RegimeState, SignalVector

REGIME_RULES: dict[RegimeLabel, dict[str, float]] = {
    RegimeLabel.EXPANSION: {
        "growth_z": 0.5,
        "inflation_z": 0.0,
        "financial_conditions_z": -0.5,
        "labor_z": 0.5,
        "yield_curve_z": 0.3,
        "vol_z": -0.5,
    },
    RegimeLabel.OVERHEATING: {
        "growth_z": 0.5,
        "inflation_z": 1.5,
        "financial_conditions_z": 0.3,
        "labor_z": 1.0,
        "policy_sentiment": 0.5,
        "vol_z": 0.0,
    },
    RegimeLabel.SLOWDOWN: {
        "growth_z": -0.5,
        "inflation_z": 0.0,
        "financial_conditions_z": 0.5,
        "labor_z": -0.5,
        "yield_curve_z": -0.3,
        "vol_z": 0.5,
    },
    RegimeLabel.CONTRACTION: {
        "growth_z": -1.5,
        "inflation_z": -0.5,
        "financial_conditions_z": 1.0,
        "labor_z": -1.5,
        "vol_z": 1.0,
    },
    RegimeLabel.CRISIS: {
        "growth_z": -2.0,
        "financial_conditions_z": 2.0,
        "vol_z": 2.0,
        "yield_curve_z": -1.0,
    },
    RegimeLabel.TRANSITION: {
        "growth_z": 0.0,
        "inflation_z": 0.0,
        "financial_conditions_z": 0.0,
        "labor_z": 0.0,
    },
}


def _regime_affinity(signal: SignalVector, prototype: dict[str, float]) -> float:
    sig_dict = signal.model_dump(exclude={"date"})
    total = 0.0
    for key, target in prototype.items():
        val = sig_dict.get(key, 0.0)
        total -= (val - target) ** 2
    return total


def _softmax(scores: dict[RegimeLabel, float]) -> dict[RegimeLabel, float]:
    max_score = max(scores.values())
    exp_scores = {k: math.exp(v - max_score) for k, v in scores.items()}
    total = sum(exp_scores.values())
    return {k: v / total for k, v in exp_scores.items()}


def _top_drivers(signal: SignalVector, label: RegimeLabel) -> list[dict[str, object]]:
    proto = REGIME_RULES[label]
    sig_dict = signal.model_dump(exclude={"date"})
    drivers = []
    for key, target in proto.items():
        val = sig_dict.get(key, 0.0)
        gap = abs(val - target)
        drivers.append({
            "signal": key,
            "observed": round(val, 3),
            "prototype": target,
            "gap": round(gap, 3),
        })
    drivers.sort(key=lambda d: d["gap"])  # type: ignore[arg-type]
    return drivers[:4]


def classify_regime(
    signal: SignalVector,
    previous: RegimeState | None = None,
) -> RegimeState:
    affinities = {
        label: _regime_affinity(signal, proto)
        for label, proto in REGIME_RULES.items()
    }
    probs = _softmax(affinities)
    label = max(probs, key=probs.__getitem__)
    confidence = probs[label]

    prev_label = previous.label if previous else None
    transition = prev_label is not None and label != prev_label

    return RegimeState(
        date=signal.date,
        label=label,
        confidence=round(confidence, 4),
        probabilities={k.value: round(v, 4) for k, v in probs.items()},
        drivers=_top_drivers(signal, label),
        previous_label=prev_label,
        transition_detected=transition,
    )
