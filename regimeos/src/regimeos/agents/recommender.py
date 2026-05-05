"""Recommendation agent — converts a regime state to actionable risk guidance.

The agent applies regime-specific rule templates, then optionally
enriches the rationale via LLM. Human approval is required before
any recommendation is considered final.
"""

from __future__ import annotations

from datetime import datetime, timezone

from regimeos.models.regime import RegimeLabel, RegimeState
from regimeos.models.recommendation import Recommendation, RiskAction

REGIME_PLAYBOOKS: dict[RegimeLabel, dict[str, list]] = {
    RegimeLabel.EXPANSION: {
        "actions": [RiskAction.HOLD_STEADY, RiskAction.INCREASE_EQUITY_EXPOSURE],
        "watchlist": ["inflation breakevens", "yield curve slope", "credit spreads"],
        "scenarios": ["overheating transition", "policy normalization"],
    },
    RegimeLabel.OVERHEATING: {
        "actions": [RiskAction.REDUCE_DURATION, RiskAction.REDUCE_EQUITY_EXPOSURE, RiskAction.INCREASE_HEDGES],
        "watchlist": ["CPI components", "Fed dot plot", "short-rate pricing"],
        "scenarios": ["aggressive hiking cycle", "demand destruction", "hard landing"],
    },
    RegimeLabel.SLOWDOWN: {
        "actions": [RiskAction.EXTEND_DURATION, RiskAction.ADD_LIQUIDITY_BUFFER, RiskAction.TIGHTEN_CREDIT],
        "watchlist": ["labor market leading indicators", "credit conditions", "earnings revisions"],
        "scenarios": ["soft landing", "contraction", "policy pivot"],
    },
    RegimeLabel.CONTRACTION: {
        "actions": [RiskAction.REDUCE_EQUITY_EXPOSURE, RiskAction.ADD_LIQUIDITY_BUFFER,
                    RiskAction.EXTEND_DURATION, RiskAction.REDUCE_HEDGES],
        "watchlist": ["credit spreads", "bank lending standards", "fiscal response"],
        "scenarios": ["recovery timing", "policy stimulus effectiveness"],
    },
    RegimeLabel.CRISIS: {
        "actions": [RiskAction.REDUCE_EQUITY_EXPOSURE, RiskAction.ADD_LIQUIDITY_BUFFER,
                    RiskAction.INCREASE_HEDGES, RiskAction.REVIEW_ASSUMPTIONS],
        "watchlist": ["funding markets", "central bank facilities", "contagion signals"],
        "scenarios": ["policy backstop", "systemic transmission", "recovery path"],
    },
    RegimeLabel.TRANSITION: {
        "actions": [RiskAction.HOLD_STEADY, RiskAction.REVIEW_ASSUMPTIONS],
        "watchlist": ["directional signal confirmation", "leading indicators"],
        "scenarios": ["regime confirmation", "false signal"],
    },
}


def _build_rationale(state: RegimeState) -> str:
    driver_text = ", ".join(
        f"{d['signal']} ({d['observed']:+.2f})" for d in state.drivers[:3]
    )
    transition_note = ""
    if state.transition_detected and state.previous_label:
        transition_note = (
            f" This represents a transition from {state.previous_label.value}. "
            "Confirm with additional data before acting."
        )

    return (
        f"Regime classified as {state.label.value} (confidence: {state.confidence:.0%}). "
        f"Key signals: {driver_text}.{transition_note} "
        f"This recommendation is draft decision support — ALCO approval required before execution."
    )


def generate_recommendation(state: RegimeState) -> Recommendation:
    playbook = REGIME_PLAYBOOKS.get(state.label, REGIME_PLAYBOOKS[RegimeLabel.TRANSITION])

    return Recommendation(
        regime=state.label.value,
        confidence=state.confidence,
        actions=playbook["actions"],
        rationale=_build_rationale(state),
        watchlist=playbook["watchlist"],
        scenario_priorities=playbook["scenarios"],
        generated_at=datetime.now(timezone.utc).isoformat(),
        approval_status="pending",
    )
