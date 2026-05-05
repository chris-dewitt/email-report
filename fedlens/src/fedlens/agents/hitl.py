"""HITL (Human-in-the-Loop) review queue for agent outputs."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from fedlens.agents.base import AgentTrace
from fedlens.storage.paths import reviews_dir


@dataclass
class ReviewItem:
    """An item in the review queue."""

    review_id: str
    trace: dict
    submitted_at: str
    reviewed_at: str | None = None
    status: str = "pending"  # pending, approved, rejected
    reviewer_comment: str | None = None


class ReviewQueue:
    """JSONL-backed HITL review queue."""

    def __init__(self, path: Path | None = None):
        self._path = path or (reviews_dir() / "review_queue.jsonl")
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def submit(self, trace: AgentTrace) -> str:
        """Submit an agent trace for review. Returns review_id."""
        review_id = str(uuid.uuid4())[:8]

        item = ReviewItem(
            review_id=review_id,
            trace=trace.to_dict(),
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )

        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(item), default=str) + "\n")

        return review_id

    def list_pending(self) -> list[ReviewItem]:
        """List all pending review items."""
        items = self._load_all()
        return [i for i in items if i.status == "pending"]

    def list_all(self) -> list[ReviewItem]:
        """List all review items."""
        return self._load_all()

    def approve(self, review_id: str, comment: str = "") -> bool:
        """Approve a review item."""
        return self._update_status(review_id, "approved", comment)

    def reject(self, review_id: str, comment: str = "") -> bool:
        """Reject a review item."""
        return self._update_status(review_id, "rejected", comment)

    def _update_status(self, review_id: str, status: str, comment: str) -> bool:
        items = self._load_all()
        found = False
        for item in items:
            if item.review_id == review_id:
                item.status = status
                item.reviewer_comment = comment
                item.reviewed_at = datetime.now(timezone.utc).isoformat()
                found = True
                break

        if found:
            self._save_all(items)
        return found

    def _load_all(self) -> list[ReviewItem]:
        if not self._path.exists():
            return []

        items = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    items.append(ReviewItem(**data))
        return items

    def _save_all(self, items: list[ReviewItem]) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(asdict(item), default=str) + "\n")
