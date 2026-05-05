"""Market Reaction Agent — summarize market moves around a Fed communication."""

from __future__ import annotations

import polars as pl

from fedlens.agents.base import BaseAgent, AgentTrace, AgentStep
from fedlens.storage.paths import gold_dir


class ReactionAgent(BaseAgent):
    """Summarize market reactions to a Fed communication using event study data."""

    def __init__(self):
        super().__init__("reaction_agent")

    def run(self, doc_id: str) -> AgentTrace:
        trace = self._new_trace()

        # Load event study results
        es_path = gold_dir("event_study") / "results.parquet"
        if not es_path.exists():
            trace.output = {"error": "Event study results not found. Run 'fedlens event-study' first."}
            return self._complete_trace(trace)

        df = pl.read_parquet(es_path)
        doc_results = df.filter(pl.col("doc_id") == doc_id)

        if doc_results.is_empty():
            trace.output = {"error": f"No event study results for {doc_id}"}
            return self._complete_trace(trace)

        # Build structured reaction summary
        reactions = []
        for row in doc_results.iter_rows(named=True):
            reactions.append({
                "series": row["series_id"],
                "series_name": row["series_name"],
                "car": row["car"],
                "t_stat": row["t_stat"],
                "p_value": row["p_value"],
                "significant": row["p_value"] < 0.10,
            })

        # Sort by absolute CAR
        reactions.sort(key=lambda r: abs(r["car"]), reverse=True)

        trace.steps.append(AgentStep(
            tool="event_study_lookup",
            input_summary=f"Looking up event study for {doc_id}",
            output_summary=f"Found {len(reactions)} market series, {sum(1 for r in reactions if r['significant'])} significant",
        ))

        # Determine overall market reaction
        sig_reactions = [r for r in reactions if r["significant"]]
        if sig_reactions:
            top = sig_reactions[0]
            direction = "positive" if top["car"] > 0 else "negative"
            summary = f"Strongest reaction: {top['series_name']} CAR={top['car']:+.4f} (t={top['t_stat']:.2f})"
        else:
            summary = "No statistically significant market reactions detected."

        trace.output = {
            "doc_id": doc_id,
            "summary": summary,
            "reactions": reactions,
            "significant_count": len(sig_reactions),
        }
        trace.confidence = min(1.0, len(sig_reactions) / 3)
        trace.approval_status = "auto"

        return self._complete_trace(trace)
