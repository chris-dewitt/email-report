"""Generate yield curve and Fed Funds futures charts as PNG bytes."""

import io
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def render_yield_curve(curve_data: dict) -> bytes | None:
    """Render US Treasury yield curve (today vs yesterday) as PNG bytes."""
    today = curve_data.get("today", {})
    yesterday = curve_data.get("yesterday", {})

    if not today:
        logger.warning("No yield curve data to plot")
        return None

    tenors = list(today.keys())
    today_vals = [today[t] for t in tenors]
    yesterday_vals = [yesterday.get(t) for t in tenors]

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(tenors, today_vals, "o-", color="#1565c0", linewidth=2,
            markersize=5, label="Today")

    if any(v is not None for v in yesterday_vals):
        yday_clean = [v if v is not None else float("nan") for v in yesterday_vals]
        ax.plot(tenors, yday_clean, "s--", color="#9e9e9e", linewidth=1.5,
                markersize=4, label="Previous Day")

    ax.set_title("US Treasury Yield Curve", fontsize=14, fontweight="bold")
    ax.set_xlabel("Tenor")
    ax.set_ylabel("Yield (%)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def render_fed_futures_curve(futures_data: dict) -> bytes | None:
    """Render Fed Funds futures implied rate curve (today vs yesterday) as PNG bytes."""
    today = futures_data.get("today", {})
    yesterday = futures_data.get("yesterday", {})

    if not today:
        logger.warning("No Fed Funds futures data to plot")
        return None

    labels = list(today.keys())
    today_vals = [today[l] for l in labels]
    yesterday_vals = [yesterday.get(l) for l in labels]

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(labels, today_vals, "o-", color="#c62828", linewidth=2,
            markersize=5, label="Today")

    if any(v is not None for v in yesterday_vals):
        yday_clean = [v if v is not None else float("nan") for v in yesterday_vals]
        ax.plot(labels, yday_clean, "s--", color="#9e9e9e", linewidth=1.5,
                markersize=4, label="Previous Day")

    ax.set_title("Fed Funds Futures — Implied Rate", fontsize=14, fontweight="bold")
    ax.set_xlabel("Contract Month")
    ax.set_ylabel("Implied Rate (%)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()
