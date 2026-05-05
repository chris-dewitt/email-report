"""Agent orchestrator — chains agents for full document analysis."""

from __future__ import annotations

from rich.console import Console

from fedlens.agents.base import AgentTrace
from fedlens.agents.tone_agent import ToneAgent
from fedlens.agents.reaction_agent import ReactionAgent
from fedlens.agents.briefing_agent import BriefingAgent
from fedlens.agents.hitl import ReviewQueue

console = Console()


class AgentOrchestrator:
    """Orchestrate multi-agent analysis of Fed communications."""

    def __init__(self):
        self.tone_agent = ToneAgent()
        self.reaction_agent = ReactionAgent()
        self.briefing_agent = BriefingAgent()
        self.review_queue = ReviewQueue()

    def run_full_analysis(self, doc_id: str) -> dict[str, AgentTrace]:
        """Run tone → reaction → briefing pipeline for a document."""
        console.print(f"\n[bold cyan]Full analysis: {doc_id}[/bold cyan]")

        # Step 1: Tone analysis
        console.print("  [dim]Running tone agent...[/dim]")
        tone_trace = self.tone_agent.run(doc_id=doc_id)
        net = tone_trace.output.get("net_score", 0)
        console.print(f"  Tone: net_score={net:+.3f}")

        # Step 2: Market reaction
        console.print("  [dim]Running reaction agent...[/dim]")
        reaction_trace = self.reaction_agent.run(doc_id=doc_id)
        console.print(f"  Reaction: {reaction_trace.output.get('summary', 'N/A')}")

        # Step 3: Briefing (uses RAG + LLM)
        console.print("  [dim]Running briefing agent...[/dim]")
        briefing_trace = self.briefing_agent.run(
            question=f"Analyze the policy implications of {doc_id}",
            doc_id=doc_id,
        )

        # Submit briefing for HITL review
        if briefing_trace.approval_status == "pending":
            review_id = self.review_queue.submit(briefing_trace)
            console.print(f"  Briefing submitted for review: [yellow]{review_id}[/yellow]")

        return {
            "tone": tone_trace,
            "reaction": reaction_trace,
            "briefing": briefing_trace,
        }
