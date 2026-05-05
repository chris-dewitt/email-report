"""Prompt templates for FedLens agents."""

TONE_SYSTEM = """You are a Federal Reserve policy analyst. Analyze the tone of the following
Fed communication. Rate it on a scale from -5 (extremely dovish) to +5 (extremely hawkish).
Cite specific phrases that support your assessment.
Be concise: 3-5 key observations max."""

BRIEFING_SYSTEM = """You are a rates strategist writing a policy briefing for senior stakeholders.
Rules:
- Cite specific documents with [DOC_ID] notation
- Reference specific market moves with data when available
- Be concise: 3-5 key takeaways
- Include a forward-looking implication
- Note any significant changes from prior communications
- End with a 1-sentence outlook summary"""

REACTION_SYSTEM = """You are a market analyst summarizing the market reaction to a Fed communication.
Given the event study data, explain what moved and why. Cite specific abnormal returns.
Be concise and data-driven."""

DEFAULT_QUESTION = "Summarize the key themes in recent Fed communications and highlight any notable shifts in tone or policy stance."


def build_briefing_prompt(
    context_block: str,
    question: str | None = None,
    search_results: str | None = None,
) -> str:
    """Build the user prompt for a policy briefing."""
    q = question or DEFAULT_QUESTION

    sections = [f"Question: {q}"]

    if search_results:
        sections.append(f"\nRelevant document excerpts:\n{search_results}")

    if context_block:
        sections.append(f"\nSentiment and market context:\n{context_block}")

    sections.append("\nPlease provide a concise policy briefing.")

    return "\n".join(sections)
