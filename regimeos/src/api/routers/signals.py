from __future__ import annotations

from fastapi import APIRouter

from regimeos.models.regime import SignalVector
from regimeos.signals.sample import get_sample_signals

router = APIRouter()


@router.get("", response_model=list[SignalVector])
def list_signals() -> list[SignalVector]:
    return get_sample_signals()


@router.get("/latest", response_model=SignalVector)
def latest_signal() -> SignalVector:
    return get_sample_signals()[-1]


@router.post("", response_model=SignalVector)
def submit_signal(signal: SignalVector) -> SignalVector:
    return signal
