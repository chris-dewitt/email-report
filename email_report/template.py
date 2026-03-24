"""Render the HTML email template using Jinja2."""

from datetime import datetime
from pathlib import Path

from markupsafe import Markup
from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = Path(__file__).parent / "templates"


def render_email(
    rates_html: str,
    yield_curve_cid: str | None,
    fed_futures_cid: str | None,
    fed_links: list[dict],
    econ_links: list[dict],
    ai_news: list[dict],
    errors: list[str],
    report_date: str | None = None,
) -> str:
    """Render the daily report HTML email."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=True,
    )
    template = env.get_template("daily_report.html")

    if report_date is None:
        report_date = datetime.now().strftime("%A, %B %d, %Y")

    return template.render(
        report_date=report_date,
        rates_html=Markup(rates_html),
        yield_curve_cid=yield_curve_cid,
        fed_futures_cid=fed_futures_cid,
        fed_links=fed_links,
        econ_links=econ_links,
        ai_news=ai_news,
        errors=errors,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
