"""Build an HTML table of interest rates with daily changes."""

import pandas as pd


def _fmt_rate(value: float) -> str:
    return f"{value:.2f}%"


def _fmt_change(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f} bps"


def _change_color(value: float) -> str:
    if value > 0:
        return "#d32f2f"  # red — rates rising
    if value < 0:
        return "#388e3c"  # green — rates falling
    return "#666666"


def build_rates_html(df: pd.DataFrame) -> str:
    """Build an HTML table from rates DataFrame grouped by category."""
    if df.empty:
        return '<p style="color:#999;">Rate data unavailable.</p>'

    lines = [
        '<table cellpadding="6" cellspacing="0" '
        'style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;font-size:13px;">',
        "<thead>",
        '<tr style="background:#1a237e;color:#fff;">',
        '<th style="text-align:left;padding:8px;">Rate</th>',
        '<th style="text-align:right;padding:8px;">Current</th>',
        '<th style="text-align:right;padding:8px;">Previous</th>',
        '<th style="text-align:right;padding:8px;">Change (bps)</th>',
        "</tr>",
        "</thead>",
        "<tbody>",
    ]

    categories = df["category"].unique()
    for cat in categories:
        lines.append(
            f'<tr><td colspan="4" style="background:#e8eaf6;font-weight:bold;'
            f'padding:6px 8px;border-top:1px solid #ccc;">{cat}</td></tr>'
        )
        subset = df[df["category"] == cat]
        for _, row in subset.iterrows():
            change_bps = row["change"] * 100
            color = _change_color(change_bps)
            lines.append(
                f'<tr style="border-bottom:1px solid #eee;">'
                f'<td style="padding:6px 8px;">{row["label"]}</td>'
                f'<td style="text-align:right;padding:6px 8px;font-family:monospace;">'
                f'{_fmt_rate(row["current"])}</td>'
                f'<td style="text-align:right;padding:6px 8px;font-family:monospace;">'
                f'{_fmt_rate(row["previous"])}</td>'
                f'<td style="text-align:right;padding:6px 8px;font-family:monospace;color:{color};">'
                f'{_fmt_change(change_bps)}</td>'
                f"</tr>"
            )

    lines.append("</tbody></table>")
    return "\n".join(lines)
