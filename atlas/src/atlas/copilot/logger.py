"""Audit logger for copilot LLM calls — writes to JSONL."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from atlas.storage.paths import copilot_log_path


def log_copilot_call(
    prompt: str,
    response: str,
    model: str,
    citations: list[str] | None = None,
    tokens_prompt: int = 0,
    tokens_response: int = 0,
    approval_state: str = "auto",
) -> None:
    """Append a copilot call record to the JSONL log file."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "prompt": prompt[:2000],  # Truncate very long prompts
        "response": response[:5000],
        "tokens_prompt": tokens_prompt,
        "tokens_response": tokens_response,
        "citations": citations or [],
        "approval_state": approval_state,
    }

    log_path = copilot_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as f:
        f.write(json.dumps(record) + "\n")
