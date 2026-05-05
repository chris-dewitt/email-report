"""Base agent framework for FedLens — structured outputs, traces, HITL."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
import time


@dataclass
class Citation:
    """A citation referencing a specific document chunk."""

    doc_id: str
    chunk_id: str | None = None
    text_excerpt: str = ""
    relevance_score: float = 0.0


@dataclass
class AgentStep:
    """A single step in an agent's execution trace."""

    tool: str  # "search", "event_study", "llm_generate", "sentiment", etc.
    input_summary: str
    output_summary: str
    duration_ms: int = 0


@dataclass
class AgentTrace:
    """Complete trace of an agent's execution."""

    agent_name: str
    started_at: str = ""
    completed_at: str = ""
    steps: list[AgentStep] = field(default_factory=list)
    output: dict = field(default_factory=dict)
    confidence: float = 0.0
    citations: list[Citation] = field(default_factory=list)
    approval_status: str = "auto"  # "pending", "approved", "rejected", "auto"
    reviewer_comment: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class BaseAgent(ABC):
    """Base class for all FedLens agents."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, **kwargs) -> AgentTrace:
        """Execute the agent and return a trace."""
        ...

    def _new_trace(self) -> AgentTrace:
        return AgentTrace(
            agent_name=self.name,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

    def _complete_trace(self, trace: AgentTrace) -> AgentTrace:
        trace.completed_at = datetime.now(timezone.utc).isoformat()
        return trace

    def _call_llm(self, prompt: str, system: str | None = None) -> tuple[str, AgentStep]:
        """Call Ollama and return response + step trace."""
        from fedlens.copilot.ollama_client import OllamaClient

        start = time.time()
        client = OllamaClient()
        result = client.generate(prompt, system=system)
        elapsed = int((time.time() - start) * 1000)

        step = AgentStep(
            tool="llm_generate",
            input_summary=prompt[:200] + "..." if len(prompt) > 200 else prompt,
            output_summary=result["response"][:200] + "..." if len(result["response"]) > 200 else result["response"],
            duration_ms=elapsed,
        )
        return result["response"], step

    def _search(self, query: str, k: int = 5) -> tuple[list, AgentStep]:
        """Run semantic search and return results + step trace."""
        from fedlens.models.search import semantic_search

        start = time.time()
        results = semantic_search(query, k=k)
        elapsed = int((time.time() - start) * 1000)

        step = AgentStep(
            tool="search",
            input_summary=f"Query: {query} (k={k})",
            output_summary=f"Found {len(results)} results",
            duration_ms=elapsed,
        )
        return results, step
