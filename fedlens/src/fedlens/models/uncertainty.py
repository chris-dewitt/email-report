"""Economic policy uncertainty scoring for Fed communications.

Adapted from Baker-Bloom-Davis methodology for Fed-specific text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# Uncertainty-related terms (adapted from Baker-Bloom-Davis + Fed-specific)
UNCERTAINTY_TERMS = [
    "uncertain", "uncertainty", "risk", "risks",
    "unclear", "unpredictable", "volatile", "volatility",
    "depends on", "contingent", "evolving",
    "could", "might", "may", "possibly", "potentially",
    "outlook is uncertain", "highly uncertain",
    "considerable uncertainty", "elevated uncertainty",
    "unknown", "unresolved", "challenging",
]

# Hedging / tentative language
HEDGING_TERMS = [
    "if appropriate", "as appropriate", "some",
    "somewhat", "roughly", "approximately",
    "on balance", "broadly", "generally",
    "to some extent", "in part",
]

# Forward guidance certainty markers (inverse of uncertainty)
CERTAINTY_TERMS = [
    "committed", "will continue", "determined",
    "strongly", "firmly", "confident",
    "prepared to", "stands ready",
]


@dataclass
class UncertaintyResult:
    """Result of uncertainty analysis."""

    uncertainty_score: float  # 0 to 1 (higher = more uncertain)
    hedging_score: float  # 0 to 1
    certainty_score: float  # 0 to 1
    net_uncertainty: float  # 0 to 1 (adjusted for certainty)
    uncertainty_count: int
    hedging_count: int
    certainty_count: int
    total_words: int


class UncertaintyScorer:
    """Measure uncertainty in Fed communications."""

    def __init__(self):
        self._uncertainty_patterns = [
            re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)
            for t in UNCERTAINTY_TERMS
        ]
        self._hedging_patterns = [
            re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)
            for t in HEDGING_TERMS
        ]
        self._certainty_patterns = [
            re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)
            for t in CERTAINTY_TERMS
        ]

    def score(self, text: str) -> UncertaintyResult:
        """Score text for uncertainty."""
        words = text.split()
        total = len(words)
        if total == 0:
            return UncertaintyResult(
                uncertainty_score=0, hedging_score=0, certainty_score=0,
                net_uncertainty=0, uncertainty_count=0, hedging_count=0,
                certainty_count=0, total_words=0,
            )

        u_count = sum(len(p.findall(text)) for p in self._uncertainty_patterns)
        h_count = sum(len(p.findall(text)) for p in self._hedging_patterns)
        c_count = sum(len(p.findall(text)) for p in self._certainty_patterns)

        # Normalize by text length (per 100 words)
        u_score = min(1.0, (u_count / total) * 20)
        h_score = min(1.0, (h_count / total) * 20)
        c_score = min(1.0, (c_count / total) * 20)

        # Net uncertainty adjusted for certainty markers
        net = max(0.0, min(1.0, (u_score + h_score * 0.5 - c_score * 0.5)))

        return UncertaintyResult(
            uncertainty_score=round(u_score, 4),
            hedging_score=round(h_score, 4),
            certainty_score=round(c_score, 4),
            net_uncertainty=round(net, 4),
            uncertainty_count=u_count,
            hedging_count=h_count,
            certainty_count=c_count,
            total_words=total,
        )
