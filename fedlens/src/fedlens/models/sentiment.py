"""Hawkish/Dovish sentiment scoring for Fed communications."""

from __future__ import annotations

import re
from dataclasses import dataclass

# --- Curated hawkish/dovish dictionaries ---
# Based on financial NLP literature (Loughran-McDonald) + Fed-specific terms

HAWKISH_TERMS = [
    "inflation", "inflationary", "elevated", "upside risk", "price stability",
    "tighten", "tightening", "restrictive", "raise", "hike", "hiking",
    "overheating", "overshoot", "above target", "price pressures",
    "strong labor", "tight labor", "robust", "solid pace",
    "reduce the size", "balance sheet reduction", "tapering",
    "further increases", "ongoing increases", "sufficiently restrictive",
    "data dependent", "remain elevated", "higher for longer",
    "upward pressure", "broadened", "persistent",
    "reduce its holdings", "vigilant",
]

DOVISH_TERMS = [
    "accommodate", "accommodative", "support", "supporting",
    "downside risk", "patient", "below target", "subdued",
    "gradual", "ease", "easing", "lower", "cut", "cutting",
    "stimulate", "stimulus", "recovery", "weak", "weakness",
    "slack", "softening", "deteriorat", "contraction",
    "muted", "below maximum", "below longer-run",
    "maintain the target", "maintain its target",
    "reinvesting", "purchase", "purchasing",
    "favorable", "well anchored", "transitory",
    "slower pace", "moderate", "moderation",
    "gained greater confidence", "sustainable",
]


@dataclass
class SentimentResult:
    """Result of hawkish/dovish analysis."""

    hawkish_score: float  # 0 to 1
    dovish_score: float  # 0 to 1
    net_score: float  # hawkish - dovish, range [-1, 1]
    confidence: float  # 0 to 1
    method: str  # "dictionary", "llm", "combined"
    hawkish_count: int
    dovish_count: int
    total_terms: int
    cited_hawkish: list[str]
    cited_dovish: list[str]


class SentimentScorer:
    """Score Fed communications for hawkish/dovish tone."""

    def __init__(self):
        # Pre-compile patterns
        self._hawkish_patterns = [
            re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
            for term in HAWKISH_TERMS
        ]
        self._dovish_patterns = [
            re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
            for term in DOVISH_TERMS
        ]

    def score_dictionary(self, text: str) -> SentimentResult:
        """Score using dictionary-based approach."""
        words = text.lower().split()
        total = len(words)
        if total == 0:
            return SentimentResult(
                hawkish_score=0, dovish_score=0, net_score=0,
                confidence=0, method="dictionary",
                hawkish_count=0, dovish_count=0, total_terms=0,
                cited_hawkish=[], cited_dovish=[],
            )

        # Count matches
        hawkish_hits = []
        for pattern in self._hawkish_patterns:
            matches = pattern.findall(text)
            hawkish_hits.extend(matches)

        dovish_hits = []
        for pattern in self._dovish_patterns:
            matches = pattern.findall(text)
            dovish_hits.extend(matches)

        h_count = len(hawkish_hits)
        d_count = len(dovish_hits)
        total_sentiment = h_count + d_count

        if total_sentiment == 0:
            return SentimentResult(
                hawkish_score=0.5, dovish_score=0.5, net_score=0,
                confidence=0, method="dictionary",
                hawkish_count=0, dovish_count=0, total_terms=total,
                cited_hawkish=[], cited_dovish=[],
            )

        h_score = h_count / total_sentiment
        d_score = d_count / total_sentiment
        net = h_score - d_score

        # Confidence based on total matches relative to text length
        coverage = total_sentiment / (total / 10)  # expect ~1 sentiment term per 10 words
        confidence = min(1.0, coverage)

        # Unique cited terms
        cited_h = sorted(set(t.lower() for t in hawkish_hits))[:10]
        cited_d = sorted(set(t.lower() for t in dovish_hits))[:10]

        return SentimentResult(
            hawkish_score=round(h_score, 4),
            dovish_score=round(d_score, 4),
            net_score=round(net, 4),
            confidence=round(confidence, 4),
            method="dictionary",
            hawkish_count=h_count,
            dovish_count=d_count,
            total_terms=total_sentiment,
            cited_hawkish=cited_h,
            cited_dovish=cited_d,
        )
