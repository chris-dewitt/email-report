"""Send HTML email with inline images via Gmail SMTP."""

import logging
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

logger = logging.getLogger(__name__)


def send_email(
    smtp_config: dict,
    recipients: list[str],
    subject: str,
    html_body: str,
    inline_images: dict[str, bytes] | None = None,
) -> None:
    """Send an HTML email with optional inline images via SMTP.

    Args:
        smtp_config: dict with host, port, sender, password.
        recipients: list of email addresses.
        subject: email subject line.
        html_body: rendered HTML string.
        inline_images: mapping of Content-ID to PNG bytes.
    """
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = smtp_config["sender"]
    msg["To"] = ", ".join(recipients)

    msg.attach(MIMEText(html_body, "html"))

    if inline_images:
        for cid, img_bytes in inline_images.items():
            img = MIMEImage(img_bytes, _subtype="png")
            img.add_header("Content-ID", f"<{cid}>")
            img.add_header("Content-Disposition", "inline", filename=f"{cid}.png")
            msg.attach(img)

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"], timeout=30) as server:
            server.starttls()
            server.login(smtp_config["sender"], smtp_config["password"])
            server.sendmail(smtp_config["sender"], recipients, msg.as_string())
        logger.info("Email sent successfully to %s", recipients)
    except Exception:
        logger.exception("Failed to send email")
        # Save HTML fallback
        fallback = Path("logs/last_report.html")
        fallback.parent.mkdir(exist_ok=True)
        fallback.write_text(html_body, encoding="utf-8")
        logger.info("Saved fallback HTML to %s", fallback)
        raise
