"""State explainer — generates a human-readable regime briefing.

Falls back to a structured template if the LLM is unavailable.
"""

from __future__ import annotations

import json

import httpx

from regimeos.models.regime import RegimeState
from regimeos.settings import settings

SYSTEM_PROMPT = """You are a senior macro strategist. Given a regime classification
and signal data, write a 2-3 paragraph briefing for a senior investment committee:
1. What regime we are in and why the signals support it
2. What changed since the previous period (if a transition occurred)
3. What decision-makers should be monitoring most closely

Be precise, reference the signal values, and be explicit about uncertainty."""


def explain_state(state: RegimeState, question: str | None = None) -> str:
    context = json.dumps(state.model_dump(), indent=2, default=str)
    prompt = f"Regime state:\n{context}"
    if question:
        prompt += f"\n\nFollow-up question: {question}"

    try:
        resp = httpx.post(
            f"{settings.ollama_url}/api/generate",
            json={"model": settings.ollama_model, "system": SYSTEM_PROMPT, "prompt": prompt, "stream": False},
            timeout=90.0,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except (httpx.HTTPError, KeyError):
        return _fallback_explanation(state)


def _fallback_explanation(state: RegimeState) -> str:
    probs = state.probabilities
    top_alt = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]

    lines = [
        f"**Current Regime: {state.label.value.upper()}** (confidence: {state.confidence:.0%})",
        "",
        f"The macro signal composite places us in {state.label.value} with "
        f"{state.confidence:.0%} confidence. "
        + (
            f"This is a transition from {state.previous_label.value}. "
            "Expect elevated signal noise during regime shift."
            if state.transition_detected and state.previous_label
            else "The regime has been stable."
        ),
        "",
        "**Top regime signals:** " + ", ".join(
            f"{d['signal']} = {d['observed']:+.2f}" for d in state.drivers[:4]
        ),
        "",
        "**Regime probabilities:** " + " | ".join(f"{k}: {v:.0%}" for k, v in top_alt),
        "",
        "_This is system-generated analysis. Human review required before any portfolio action._",
    ]
    return "\n".join(lines)
