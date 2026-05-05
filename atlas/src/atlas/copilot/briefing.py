"""Macro briefing generator — builds context from DuckDB, calls Ollama."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from atlas.copilot.ollama_client import OllamaClient
from atlas.copilot.prompts import SYSTEM_PROMPT, build_briefing_prompt
from atlas.copilot.logger import log_copilot_call
from atlas.ingest.registry import SERIES_MAP, Theme, get_series_by_theme
from atlas.storage.parquet_store import read_gold


def _build_context_block(lookback_days: int = 7) -> str:
    """Build a structured context block from the latest gold features."""
    lines: list[str] = []

    for theme in Theme:
        df = read_gold(theme.value, sub="features")
        if df is None or df.is_empty():
            continue

        lines.append(f"\n{theme.value.upper()}:")

        series_ids = df["series_id"].unique().to_list()
        for sid in series_ids:
            sd = SERIES_MAP.get(sid)
            if sd is None:
                continue

            subset = df.filter(df["series_id"] == sid).sort("date")
            if subset.is_empty():
                continue

            last = subset.tail(1)
            value = last["value"][0] if "value" in last.columns else None
            z = last["value_zscore"][0] if "value_zscore" in last.columns else None

            if value is not None:
                z_str = f"z={z:.2f}" if z is not None else "z=N/A"
                lines.append(f"  - {sd.name}: {value:.2f} ({z_str}) [{sid}]")

    # Add regime if available
    regime_df = read_gold("snapshot", sub="regime")
    if regime_df is not None and not regime_df.is_empty():
        last_regime = regime_df.tail(1)
        regime = last_regime["regime"][0]
        conf = last_regime["confidence"][0]
        lines.append(f"\nCurrent regime: {regime.upper()} (confidence: {conf:.0%})")

    return "\n".join(lines) if lines else "No feature data available."


def _extract_citations(text: str) -> list[str]:
    """Extract [SERIES_ID] citations from the response text."""
    pattern = r"\[([A-Z0-9_^=.\-]+)\]"
    matches = re.findall(pattern, text)
    # Filter to known series
    return [m for m in set(matches) if m in SERIES_MAP]


def generate_briefing(
    question: str | None = None,
    lookback_days: int = 7,
) -> dict:
    """Generate a macro briefing using Ollama.

    Returns dict: { summary, citations, model_used, generated_at }
    """
    context = _build_context_block(lookback_days)
    prompt = build_briefing_prompt(context, question)

    client = OllamaClient()
    result = client.generate(prompt, system=SYSTEM_PROMPT)

    summary = result.get("response", "")
    citations = _extract_citations(summary)
    model_used = result.get("model", client.model)

    output = {
        "summary": summary,
        "citations": citations,
        "model_used": model_used,
        "prompt_tokens": result.get("prompt_eval_count", 0),
        "response_tokens": result.get("eval_count", 0),
        "generated_at": datetime.now(timezone.utc),
    }

    # Log the call
    log_copilot_call(
        prompt=prompt,
        response=summary,
        model=model_used,
        citations=citations,
        tokens_prompt=output["prompt_tokens"],
        tokens_response=output["response_tokens"],
    )

    return output
