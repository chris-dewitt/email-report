"""Policy Tone Agent — assess hawkish/dovish tone of a document."""

from __future__ import annotations

import polars as pl

from fedlens.agents.base import BaseAgent, AgentTrace, AgentStep, Citation
from fedlens.agents.prompts import TONE_SYSTEM
from fedlens.models.sentiment import SentimentScorer
from fedlens.storage.paths import silver_dir


class ToneAgent(BaseAgent):
    """Analyze the tone of a Fed communication."""

    def __init__(self):
        super().__init__("tone_agent")
        self._scorer = SentimentScorer()

    def run(self, doc_id: str) -> AgentTrace:
        trace = self._new_trace()

        # Step 1: Load document text
        text = self._load_document_text(doc_id)
        if text is None:
            trace.output = {"error": f"Document {doc_id} not found"}
            trace.confidence = 0.0
            return self._complete_trace(trace)

        # Step 2: Dictionary-based sentiment
        result = self._scorer.score_dictionary(text)
        trace.steps.append(AgentStep(
            tool="sentiment_dictionary",
            input_summary=f"Scoring {doc_id} ({len(text)} chars)",
            output_summary=f"Net score: {result.net_score:+.3f} (hawk={result.hawkish_count}, dove={result.dovish_count})",
        ))

        trace.output = {
            "doc_id": doc_id,
            "net_score": result.net_score,
            "hawkish_score": result.hawkish_score,
            "dovish_score": result.dovish_score,
            "hawkish_count": result.hawkish_count,
            "dovish_count": result.dovish_count,
            "cited_hawkish": result.cited_hawkish,
            "cited_dovish": result.cited_dovish,
            "method": result.method,
        }
        trace.confidence = result.confidence
        trace.approval_status = "auto"

        return self._complete_trace(trace)

    def _load_document_text(self, doc_id: str) -> str | None:
        parsed_dir = silver_dir("parsed")
        for pq in parsed_dir.glob("*.parquet"):
            df = pl.read_parquet(pq)
            matched = df.filter(pl.col("doc_id") == doc_id)
            if not matched.is_empty():
                return " ".join(matched["text"].to_list())
        return None
