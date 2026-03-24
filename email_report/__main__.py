"""Entry point for the daily financial email report.

Usage: python -m email_report [--config email_config.yaml]
"""

import argparse
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        log_dir / "email_report.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)


def main() -> int:
    parser = argparse.ArgumentParser(description="Send daily financial email report")
    parser.add_argument(
        "--config", default="email_config.yaml",
        help="Path to email config YAML file",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Generate report but save to file instead of sending",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Run even on weekends/holidays",
    )
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    # Skip weekends
    today = datetime.now()
    if today.weekday() >= 5 and not args.force:
        logger.info("Skipping — today is %s", today.strftime("%A"))
        return 0

    logger.info("Starting daily financial email report")

    # Import here so logging is configured first
    from .config import load_email_config
    from .data_fetch import fetch_all
    from .rates_table import build_rates_html
    from .charts import render_yield_curve, render_fed_futures_curve
    from .news_feeds import fetch_fed_publications, fetch_econ_analysis, fetch_ai_news
    from .template import render_email
    from .mailer import send_email

    # Load config
    try:
        config = load_email_config(args.config)
    except Exception:
        logger.exception("Failed to load config")
        return 1

    # Fetch financial data
    logger.info("Fetching financial data...")
    data = fetch_all(config)
    errors = data["errors"]

    # Build rates table
    rates_html = build_rates_html(data["rates_df"])

    # Generate charts
    yield_curve_png = render_yield_curve(data["yield_curve"])
    fed_futures_png = render_fed_futures_curve(data["fed_futures"])

    # Fetch news feeds
    feeds_config = config.get("feeds", {})

    logger.info("Fetching news feeds...")
    fed_links = fetch_fed_publications(feeds_config.get("fed_publications", []))
    econ_links = fetch_econ_analysis(feeds_config.get("econ_analysis", []))
    ai_news = fetch_ai_news(feeds_config.get("ai_news", []))

    # Prepare inline images
    inline_images = {}
    yield_curve_cid = None
    fed_futures_cid = None

    if yield_curve_png:
        yield_curve_cid = "yield_curve_chart"
        inline_images[yield_curve_cid] = yield_curve_png

    if fed_futures_png:
        fed_futures_cid = "fed_futures_chart"
        inline_images[fed_futures_cid] = fed_futures_png

    # Render HTML
    report_date = today.strftime("%A, %B %d, %Y")
    html_body = render_email(
        rates_html=rates_html,
        yield_curve_cid=yield_curve_cid,
        fed_futures_cid=fed_futures_cid,
        fed_links=fed_links,
        econ_links=econ_links,
        ai_news=ai_news,
        errors=errors,
        report_date=report_date,
    )

    if args.dry_run:
        out_path = Path("logs/last_report.html")
        out_path.parent.mkdir(exist_ok=True)
        out_path.write_text(html_body, encoding="utf-8")
        logger.info("Dry run — saved report to %s", out_path)
        return 0

    # Send email
    smtp_config = config.get("smtp", {})
    recipients = smtp_config.get("recipients", [])
    if not recipients:
        logger.error("No recipients configured")
        return 1

    subject = f"Daily Financial Brief — {today.strftime('%b %d, %Y')}"

    try:
        send_email(smtp_config, recipients, subject, html_body, inline_images)
    except Exception:
        logger.exception("Email sending failed")
        return 1

    logger.info("Daily report completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
