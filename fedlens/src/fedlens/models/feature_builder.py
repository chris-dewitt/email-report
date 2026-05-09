"""NLP feature pipeline — sentiment, uncertainty, drift for all documents."""

from __future__ import annotations

import polars as pl
from rich.console import Console
from rich.progress import track

from fedlens.models.sentiment import SentimentScorer
from fedlens.models.uncertainty import UncertaintyScorer
from fedlens.models.drift import build_drift_features
from fedlens.storage.paths import silver_dir, gold_dir

console = Console()


def build_all_features() -> None:
    """Run the full NLP feature pipeline: sentiment + uncertainty + drift."""
    console.print("\n[bold cyan]Building NLP features...[/bold cyan]")

    _build_sentiment_features()
    _build_uncertainty_features()
    build_drift_features()

    console.print("\n[bold green]NLP feature pipeline complete.[/bold green]")


def _build_sentiment_features() -> None:
    """Score all documents for hawkish/dovish sentiment."""
    console.print("\n  [cyan]Sentiment scoring...[/cyan]")
    scorer = SentimentScorer()

    parsed_dir = silver_dir("parsed")
    if not parsed_dir.exists():
        console.print("  [red]No parsed chunks found.[/red]")
        return

    for pq in parsed_dir.glob("*.parquet"):
        dtype = pq.stem
        df = pl.read_parquet(pq)

        # Score per document (aggregate chunks per doc)
        doc_groups = df.group_by("doc_id").agg([
            pl.col("text").str.concat(" ").alias("full_text"),
            pl.col("date").first(),
            pl.col("doc_type").first(),
        ])

        results = []
        for row in track(
            doc_groups.iter_rows(named=True),
            description=f"    {dtype}",
            total=len(doc_groups),
        ):
            result = scorer.score_dictionary(row["full_text"])
            results.append({
                "doc_id": row["doc_id"],
                "date": row["date"],
                "doc_type": row["doc_type"],
                "hawkish_score": result.hawkish_score,
                "dovish_score": result.dovish_score,
                "net_score": result.net_score,
                "confidence": result.confidence,
                "hawkish_count": result.hawkish_count,
                "dovish_count": result.dovish_count,
                "total_terms": result.total_terms,
                "method": result.method,
            })

        if results:
            result_df = pl.DataFrame(results).sort("date")
            out_dir = gold_dir("sentiment")
            out_dir.mkdir(parents=True, exist_ok=True)
            result_df.write_parquet(out_dir / f"{dtype}.parquet")
            console.print(f"    Gold/sentiment/{dtype}: [yellow]{len(result_df)}[/yellow] documents")


def _build_uncertainty_features() -> None:
    """Score all documents for uncertainty."""
    console.print("\n  [cyan]Uncertainty scoring...[/cyan]")
    scorer = UncertaintyScorer()

    parsed_dir = silver_dir("parsed")
    if not parsed_dir.exists():
        return

    for pq in parsed_dir.glob("*.parquet"):
        dtype = pq.stem
        df = pl.read_parquet(pq)

        doc_groups = df.group_by("doc_id").agg([
            pl.col("text").str.concat(" ").alias("full_text"),
            pl.col("date").first(),
            pl.col("doc_type").first(),
        ])

        results = []
        for row in doc_groups.iter_rows(named=True):
            result = scorer.score(row["full_text"])
            results.append({
                "doc_id": row["doc_id"],
                "date": row["date"],
                "doc_type": row["doc_type"],
                "uncertainty_score": result.uncertainty_score,
                "hedging_score": result.hedging_score,
                "certainty_score": result.certainty_score,
                "net_uncertainty": result.net_uncertainty,
                "uncertainty_count": result.uncertainty_count,
                "hedging_count": result.hedging_count,
                "certainty_count": result.certainty_count,
                "total_words": result.total_words,
            })

        if results:
            result_df = pl.DataFrame(results).sort("date")
            out_dir = gold_dir("sentiment")  # co-locate with sentiment
            result_df.write_parquet(out_dir / f"{dtype}_uncertainty.parquet")
            console.print(f"    Gold/sentiment/{dtype}_uncertainty: [yellow]{len(result_df)}[/yellow] documents")
