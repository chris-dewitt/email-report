"""HITL approval queue for regime recommendations."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

_queue: list[dict] = []


class ApprovalAction(BaseModel):
    recommendation_id: str
    reviewer: str
    comment: str = ""


@router.get("")
def list_queue() -> list[dict]:
    return _queue


@router.post("/submit")
def submit(item: dict) -> dict:
    item["id"] = str(len(_queue))
    item["submitted_at"] = datetime.now(timezone.utc).isoformat()
    item["approval_status"] = "pending"
    _queue.append(item)
    return item


@router.post("/approve/{item_id}")
def approve(item_id: str, action: ApprovalAction) -> dict:
    for item in _queue:
        if item["id"] == item_id:
            item["approval_status"] = "approved"
            item["reviewer"] = action.reviewer
            item["review_comment"] = action.comment
            item["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            return item
    raise HTTPException(404, f"Item {item_id} not found")


@router.post("/reject/{item_id}")
def reject(item_id: str, action: ApprovalAction) -> dict:
    for item in _queue:
        if item["id"] == item_id:
            item["approval_status"] = "rejected"
            item["reviewer"] = action.reviewer
            item["review_comment"] = action.comment
            item["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            return item
    raise HTTPException(404, f"Item {item_id} not found")
