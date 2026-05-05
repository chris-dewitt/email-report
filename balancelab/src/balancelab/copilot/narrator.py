"""Risk narrative generator — explains scenario results for senior stakeholders."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx

from balancelab.models.results import ScenarioOutput
from balancelab.settings import settings


SYSTEM_PROMPT = """You are a senior ALM risk analyst at a mid-size bank. Given scenario
analysis results, write a concise executive narrative (3-5 paragraphs) that:
1. States the scenario and its key parameters
2. Explains the NII impact — which positions drive the change and why
3. Explains the EVE impact — what the duration gap means for economic value
4. Highlights the liquidity/repricing concentrations that matter most
5. Recommends what the ALCO committee should focus on

Use precise numbers from the results. Avoid jargon without explanation. Reference
specific positions by name when they are top drivers."""


def _build_context(output: ScenarioOutput) -> str:
    return json.dumps(output.model_dump(), indent=2, default=str)


def generate_narrative(
    output: ScenarioOutput,
    question: str | None = None,
) -> dict[str, str]:
    context = _build_context(output)
    user_prompt = f"Scenario results:\n{context}"
    if question:
        user_prompt += f"\n\nAdditional question: {question}"

    try:
        resp = httpx.post(
            f"{settings.ollama_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "system": SYSTEM_PROMPT,
                "prompt": user_prompt,
                "stream": False,
            },
            timeout=120.0,
        )
        resp.raise_for_status()
        narrative = resp.json().get("response", "")
    except (httpx.HTTPError, KeyError):
        narrative = _fallback_narrative(output)

    return {
        "scenario": output.scenario_name,
        "narrative": narrative,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": settings.ollama_model,
    }


def _fallback_narrative(output: ScenarioOutput) -> str:
    nii = output.nii
    eve = output.eve
    liq = output.liquidity

    direction = "increase" if nii.delta_nii > 0 else "decrease"
    eve_dir = "increase" if eve.delta_eve > 0 else "decrease"

    lines = [
        f"**{output.scenario_name}**: Under this scenario, NII is projected to "
        f"{direction} by ${abs(nii.delta_nii):,.0f} ({nii.delta_nii_pct:+.1f}%) "
        f"over {nii.horizon_months} months.",
        f"Economic value of equity would {eve_dir} by ${abs(eve.delta_eve):,.0f} "
        f"({eve.delta_eve_pct:+.1f}%). The duration gap is {eve.duration_gap:.2f} years "
        f"(assets: {eve.asset_duration:.2f}y, liabilities: {eve.liability_duration:.2f}y).",
        f"The one-year cumulative repricing gap is ${liq.one_year_cumulative_gap:,.0f} "
        f"({liq.one_year_gap_ratio:.2%} of total assets).",
    ]

    if nii.top_drivers:
        top = nii.top_drivers[0]
        lines.append(
            f"The largest NII driver is '{top['name']}' ({top['side']}, "
            f"${top['balance']:,.0f}) contributing ${top['delta_income']:,.0f} to the change."
        )

    return "\n\n".join(lines)
