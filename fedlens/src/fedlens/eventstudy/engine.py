"""Event study engine — compute abnormal returns around Fed communications.

Core math:
    AR_t = R_t - E[R_t]
    E[R_t] = mean return over estimation window (constant-mean model)
    CAR = sum(AR_t) over post-event window
    t-stat = CAR / (sigma_AR * sqrt(window_days))
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Sequence

import numpy as np
import polars as pl
from rich.console import Console
from rich.progress import track

from fedlens.config import get_settings
from fedlens.eventstudy.market_data import (
    MARKET_SERIES,
    get_daily_returns,
    pull_market_data,
)
from fedlens.storage.paths import gold_dir, silver_dir

console = Console()


@dataclass
class EventStudyResult:
    """Result of a single event study."""

    doc_id: str
    event_date: str  # ISO format
    series_id: str
    series_name: str
    pre_window: int
    post_window: int
    actual_returns: list[float]
    expected_return: float
    abnormal_returns: list[float]
    car: float  # cumulative abnormal return
    car_pre: float  # pre-event CAR
    t_stat: float
    p_value: float
    estimation_mean: float
    estimation_std: float


class EventStudyEngine:
    """Compute abnormal returns around Fed communication events."""

    def __init__(self):
        settings = get_settings().event_study
        self.pre_window = settings.pre_window_days
        self.post_window = settings.post_window_days
        self.estimation_window = settings.estimation_window_days
        self.gap = settings.gap_days

    def run_single(
        self,
        event_date: date,
        returns_df: pl.DataFrame,
        doc_id: str,
        series_id: str,
    ) -> EventStudyResult | None:
        """Run event study for one event against one market series.

        Args:
            event_date: date of the Fed communication
            returns_df: DataFrame with columns [date, value, daily_return]
            doc_id: document identifier
            series_id: market series identifier
        """
        dates = returns_df["date"].to_list()
        rets = returns_df["daily_return"].to_list()
        date_to_idx = {d: i for i, d in enumerate(dates)}

        # Ensure event_date is a date object
        if isinstance(event_date, str):
            event_date = date.fromisoformat(event_date)

        # Find the event date in market data (or next available trading day)
        event_idx = None
        for offset in range(5):  # search up to 5 days forward
            candidate = event_date + timedelta(days=offset)
            if candidate in date_to_idx:
                event_idx = date_to_idx[candidate]
                break

        if event_idx is None:
            return None

        # Estimation window: [event - gap - estimation_window, event - gap]
        est_end = event_idx - self.gap
        est_start = est_end - self.estimation_window

        if est_start < 0 or est_end < 0:
            return None

        # Event window: [event - pre, event + post]
        win_start = event_idx - self.pre_window
        win_end = event_idx + self.post_window

        if win_start < 0 or win_end >= len(rets):
            return None

        # Estimation period returns
        est_returns = np.array(rets[est_start:est_end])
        if len(est_returns) < 20:
            return None

        expected_return = float(np.mean(est_returns))
        est_std = float(np.std(est_returns, ddof=1))

        if est_std < 1e-10:
            return None

        # Event window returns
        actual_returns = rets[win_start : win_end + 1]
        abnormal_returns = [r - expected_return for r in actual_returns]

        # Split into pre and post
        pre_ar = abnormal_returns[: self.pre_window]
        post_ar = abnormal_returns[self.pre_window :]

        car = sum(post_ar)
        car_pre = sum(pre_ar)

        # t-statistic
        n_post = len(post_ar)
        t_stat = car / (est_std * np.sqrt(n_post)) if n_post > 0 else 0.0

        # Two-tailed p-value from normal approximation
        from scipy import stats

        p_value = float(2 * (1 - stats.norm.cdf(abs(t_stat))))

        return EventStudyResult(
            doc_id=doc_id,
            event_date=event_date.isoformat(),
            series_id=series_id,
            series_name=MARKET_SERIES.get(series_id, {}).get("name", series_id),
            pre_window=self.pre_window,
            post_window=self.post_window,
            actual_returns=[round(r, 6) for r in actual_returns],
            expected_return=round(expected_return, 6),
            abnormal_returns=[round(r, 6) for r in abnormal_returns],
            car=round(car, 6),
            car_pre=round(car_pre, 6),
            t_stat=round(t_stat, 4),
            p_value=round(p_value, 4),
            estimation_mean=round(expected_return, 6),
            estimation_std=round(est_std, 6),
        )


def run_event_studies(
    series_id: str = "DGS10",
    doc_type: str = "statement",
    run_all: bool = False,
) -> None:
    """Run event studies and save results to gold layer."""
    console.print("\n[bold cyan]Running event studies...[/bold cyan]")

    # Ensure market data exists
    from fedlens.eventstudy.market_data import _market_data_dir

    market_dir = _market_data_dir()
    if not any(market_dir.glob("*.parquet")):
        console.print("  Market data not found. Pulling...")
        pull_market_data(get_settings().event_study.history_start)

    # Get document dates
    meta_dir = silver_dir("metadata")
    if not meta_dir.exists():
        console.print("[red]No document metadata. Run 'fedlens ingest' first.[/red]")
        return

    all_meta = []
    for pq in meta_dir.glob("*.parquet"):
        df = pl.read_parquet(pq)
        if doc_type != "all":
            df = df.filter(pl.col("doc_type") == doc_type)
        all_meta.append(df)

    if not all_meta:
        console.print("[red]No documents found for the specified type.[/red]")
        return

    meta_df = pl.concat(all_meta).sort("date")
    console.print(f"  Documents: [yellow]{len(meta_df)}[/yellow]")

    # Determine which series to study
    series_list = list(MARKET_SERIES.keys()) if run_all else [series_id]

    engine = EventStudyEngine()
    all_results = []

    for sid in series_list:
        returns_df = get_daily_returns(sid)
        if returns_df is None:
            console.print(f"  [red]No market data for {sid}. Skipping.[/red]")
            continue

        console.print(f"\n  [cyan]{sid} ({MARKET_SERIES[sid]['name']})[/cyan]")

        for row in track(
            meta_df.iter_rows(named=True),
            description=f"    {sid}",
            total=len(meta_df),
        ):
            event_date = row["date"]
            result = engine.run_single(
                event_date=event_date,
                returns_df=returns_df,
                doc_id=row["doc_id"],
                series_id=sid,
            )
            if result:
                all_results.append(result)

    if all_results:
        # Save to gold
        results_df = pl.DataFrame([asdict(r) for r in all_results])

        # Drop list columns for the summary parquet (keep a flat version)
        summary_df = results_df.drop(["actual_returns", "abnormal_returns"])

        out_dir = gold_dir("event_study")
        out_dir.mkdir(parents=True, exist_ok=True)
        summary_df.write_parquet(out_dir / "results.parquet")

        console.print(f"\n  Saved [yellow]{len(summary_df)}[/yellow] event study results")

        # Print top movers
        sig = summary_df.filter(pl.col("p_value") < 0.10).sort("car", descending=True)
        if not sig.is_empty():
            console.print(f"\n  [bold]Significant results (p < 0.10): {len(sig)}[/bold]")
            for row in sig.head(10).iter_rows(named=True):
                direction = "[red]+" if row["car"] > 0 else "[green]"
                console.print(
                    f"    {row['doc_id']} × {row['series_id']}: "
                    f"CAR={direction}{row['car']:.4f}[/] t={row['t_stat']:.2f} p={row['p_value']:.3f}"
                )

    console.print("\n[bold green]Event studies complete.[/bold green]")
