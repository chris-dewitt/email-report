"""Briefing Agent — generates policy briefings using RAG + Ollama."""

from __future__ import annotations

import re
import polars as pl
from rich.console import Console

from fedlens.agents.base import BaseAgent, AgentTrace, Citation
from fedlens.agents.prompts import BRIEFING_SYSTEM, build_briefing_prompt
from fedlens.storage.paths import gold_dir

console = Console()


class BriefingAgent(BaseAgent):
    """Generate policy briefings using RAG + local LLM."""

    def __init__(self):
        super().__init__("briefing_agent")

    def run(
        self,
        question: str | None = None,
        doc_id: str | None = None,
        lookback_meetings: int = 4,
    ) -> AgentTrace:
        trace = self._new_trace()

        # Step 1: Semantic search for relevant context
        search_query = question or "Recent Federal Reserve policy stance and key economic themes"
        if doc_id:
            search_query = f"{doc_id} {search_query}"

        search_results, search_step = self._search(search_query, k=8)
        trace.steps.append(search_step)

        # Build search context string
        search_context = ""
        for hit in search_results:
            search_context += f"\n[{hit.doc_id}] ({hit.date}) {hit.section_heading}:\n{hit.text[:500]}\n"
            trace.citations.append(Citation(
                doc_id=hit.doc_id,
                chunk_id=hit.chunk_id,
                text_excerpt=hit.text[:200],
                relevance_score=hit.score,
            ))

        # Step 2: Build sentiment/market context
        context_block = self._build_context_block(doc_id)

        # Step 3: Generate briefing via LLM
        prompt = build_briefing_prompt(
            context_block=context_block,
            question=question,
            search_results=search_context,
        )

        response, llm_step = self._call_llm(prompt, system=BRIEFING_SYSTEM)
        trace.steps.append(llm_step)

        # Step 4: Extract doc citations from response
        doc_refs = re.findall(r"\[(statement_\d{4}-\d{2}-\d{2})\]", response)
        for ref in set(doc_refs):
            if not any(c.doc_id == ref for c in trace.citations):
                trace.citations.append(Citation(doc_id=ref))

        trace.output = {
            "briefing": response,
            "question": question,
            "num_sources": len(search_results),
        }
        trace.confidence = min(1.0, len(trace.citations) / 3)
        trace.approval_status = "pending"  # Briefings require HITL review

        return self._complete_trace(trace)

    def _build_context_block(self, doc_id: str | None = None) -> str:
        """Build context from sentiment and event study data."""
        lines = []

        # Sentiment data
        sent_path = gold_dir("sentiment") / "statement.parquet"
        if sent_path.exists():
            sent_df = pl.read_parquet(sent_path).sort("date")
            recent = sent_df.tail(6)
            lines.append("Recent sentiment trends:")
            for row in recent.iter_rows(named=True):
                tone = "HAWKISH" if row["net_score"] > 0.1 else "DOVISH" if row["net_score"] < -0.1 else "NEUTRAL"
                lines.append(f"  {row['date']} [{row['doc_id']}]: {tone} (net={row['net_score']:+.3f})")

        # Drift data
        drift_path = gold_dir("drift") / "statement_drift.parquet"
        if drift_path.exists():
            drift_df = pl.read_parquet(drift_path).sort("date")
            recent_drift = drift_df.tail(4)
            lines.append("\nRecent language drift:")
            for row in recent_drift.iter_rows(named=True):
                alert = " ** SIGNIFICANT SHIFT **" if row["drift_score"] > 0.15 else ""
                lines.append(f"  {row['date']}: drift={row['drift_score']:.4f}{alert}")

        # Event study for specific doc
        if doc_id:
            es_path = gold_dir("event_study") / "results.parquet"
            if es_path.exists():
                es_df = pl.read_parquet(es_path).filter(pl.col("doc_id") == doc_id)
                if not es_df.is_empty():
                    lines.append(f"\nMarket reaction to {doc_id}:")
                    for row in es_df.iter_rows(named=True):
                        sig = "*" if row["p_value"] < 0.10 else ""
                        lines.append(
                            f"  {row['series_name']}: CAR={row['car']:+.4f} "
                            f"(t={row['t_stat']:.2f}, p={row['p_value']:.3f}){sig}"
                        )

        return "\n".join(lines) if lines else "No context data available."


def run_briefing(question: str | None = None, doc_id: str | None = None) -> str:
    """CLI entry point for briefing generation."""
    agent = BriefingAgent()
    trace = agent.run(question=question, doc_id=doc_id)

    if "error" in trace.output:
        return trace.output["error"]

    briefing = trace.output.get("briefing", "No briefing generated.")
    citations = [c.doc_id for c in trace.citations]

    output = f"\n{'='*60}\n"
    output += f"POLICY BRIEFING\n"
    output += f"{'='*60}\n\n"
    output += briefing
    output += f"\n\n{'─'*60}\n"
    output += f"Sources: {', '.join(set(citations))}\n"
    output += f"Confidence: {trace.confidence:.0%}\n"
    output += f"Status: {trace.approval_status}\n"
    output += f"Steps: {len(trace.steps)}\n"

    return output
