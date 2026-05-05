"""Prompt templates for the Atlas macro copilot."""

SYSTEM_PROMPT = """You are a macro research analyst at a financial institution.
You write clear, concise weekly briefings for senior decision-makers.
Rules:
- Always cite specific series IDs in square brackets, e.g. [CPIAUCSL]
- Use precise numbers from the data provided
- Be concise: 3-5 key observations max
- Note regime changes or notable threshold crossings
- Do not speculate beyond the data provided
- End with a 1-sentence outlook summary"""


DEFAULT_QUESTION = "Summarize what changed in the macro data this week and highlight the most important moves."


def build_briefing_prompt(context_block: str, question: str | None = None) -> str:
    """Build the user prompt with data context."""
    q = question or DEFAULT_QUESTION

    return f"""Here is the latest macro data summary:

{context_block}

Question: {q}

Please provide a concise briefing."""
