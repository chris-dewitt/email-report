"""Series catalog — all 36 curated macro series with metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Source(str, Enum):
    FRED = "fred"
    YFINANCE = "yfinance"


class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class Theme(str, Enum):
    INFLATION = "inflation"
    LABOR = "labor"
    RATES = "rates"
    FINANCIAL_CONDITIONS = "fincond"
    GROWTH = "growth"
    FX_MARKET = "fx_market"


@dataclass(frozen=True)
class SeriesDef:
    """Definition of a tracked macro series."""
    series_id: str          # FRED ID or yfinance ticker
    name: str               # Human-readable name
    source: Source
    frequency: Frequency
    theme: Theme
    unit: str = ""          # e.g., "percent", "index", "thousands"
    description: str = ""


# ── Full Series Catalog ─────────────────────────────────────────────────────

SERIES_CATALOG: list[SeriesDef] = [
    # ── Inflation (7) ───────────────────────────────────────────────────
    SeriesDef("CPIAUCSL", "CPI-U All Items SA", Source.FRED, Frequency.MONTHLY, Theme.INFLATION,
              "index", "Consumer Price Index for All Urban Consumers"),
    SeriesDef("CPILFESL", "Core CPI SA", Source.FRED, Frequency.MONTHLY, Theme.INFLATION,
              "index", "CPI Less Food and Energy"),
    SeriesDef("PCEPI", "PCE Price Index", Source.FRED, Frequency.MONTHLY, Theme.INFLATION,
              "index", "Personal Consumption Expenditures Price Index"),
    SeriesDef("PCEPILFE", "Core PCE", Source.FRED, Frequency.MONTHLY, Theme.INFLATION,
              "index", "PCE Excluding Food and Energy"),
    SeriesDef("T5YIE", "5Y Breakeven Inflation", Source.FRED, Frequency.DAILY, Theme.INFLATION,
              "percent", "5-Year Breakeven Inflation Rate"),
    SeriesDef("T10YIE", "10Y Breakeven Inflation", Source.FRED, Frequency.DAILY, Theme.INFLATION,
              "percent", "10-Year Breakeven Inflation Rate"),
    SeriesDef("MICH", "Michigan Inflation Expectations", Source.FRED, Frequency.MONTHLY, Theme.INFLATION,
              "percent", "University of Michigan Inflation Expectation"),

    # ── Labor (7) ───────────────────────────────────────────────────────
    SeriesDef("PAYEMS", "Nonfarm Payrolls", Source.FRED, Frequency.MONTHLY, Theme.LABOR,
              "thousands", "Total Nonfarm Payrolls"),
    SeriesDef("UNRATE", "Unemployment Rate", Source.FRED, Frequency.MONTHLY, Theme.LABOR,
              "percent", "Civilian Unemployment Rate"),
    SeriesDef("ICSA", "Initial Jobless Claims", Source.FRED, Frequency.WEEKLY, Theme.LABOR,
              "thousands", "Initial Claims, Seasonally Adjusted"),
    SeriesDef("CCSA", "Continued Claims", Source.FRED, Frequency.WEEKLY, Theme.LABOR,
              "thousands", "Continued Claims, Seasonally Adjusted"),
    SeriesDef("CES0500000003", "Avg Hourly Earnings", Source.FRED, Frequency.MONTHLY, Theme.LABOR,
              "dollars", "Average Hourly Earnings of All Employees, Total Private"),
    SeriesDef("JTSJOL", "JOLTS Job Openings", Source.FRED, Frequency.MONTHLY, Theme.LABOR,
              "thousands", "Job Openings: Total Nonfarm"),
    SeriesDef("JTSQUR", "JOLTS Quits Rate", Source.FRED, Frequency.MONTHLY, Theme.LABOR,
              "percent", "Quits Rate: Total Nonfarm"),

    # ── Rates & Treasury (7) ───────────────────────────────────────────
    SeriesDef("DFF", "Fed Funds Effective", Source.FRED, Frequency.DAILY, Theme.RATES,
              "percent", "Effective Federal Funds Rate"),
    SeriesDef("DGS2", "2Y Treasury", Source.FRED, Frequency.DAILY, Theme.RATES,
              "percent", "Market Yield on US Treasury Securities at 2-Year Constant Maturity"),
    SeriesDef("DGS10", "10Y Treasury", Source.FRED, Frequency.DAILY, Theme.RATES,
              "percent", "Market Yield on US Treasury Securities at 10-Year Constant Maturity"),
    SeriesDef("DGS30", "30Y Treasury", Source.FRED, Frequency.DAILY, Theme.RATES,
              "percent", "Market Yield on US Treasury Securities at 30-Year Constant Maturity"),
    SeriesDef("T10Y2Y", "10Y-2Y Spread", Source.FRED, Frequency.DAILY, Theme.RATES,
              "percent", "10-Year Treasury Constant Maturity Minus 2-Year"),
    SeriesDef("T10Y3M", "10Y-3M Spread", Source.FRED, Frequency.DAILY, Theme.RATES,
              "percent", "10-Year Treasury Constant Maturity Minus 3-Month"),
    SeriesDef("DFII10", "10Y TIPS Real Yield", Source.FRED, Frequency.DAILY, Theme.RATES,
              "percent", "10-Year Treasury Inflation-Indexed Security, Constant Maturity"),

    # ── Financial Conditions (6) ───────────────────────────────────────
    SeriesDef("BAMLH0A0HYM2", "HY OAS", Source.FRED, Frequency.DAILY, Theme.FINANCIAL_CONDITIONS,
              "percent", "ICE BofA US High Yield OAS"),
    SeriesDef("BAMLC0A4CBBB", "BBB OAS", Source.FRED, Frequency.DAILY, Theme.FINANCIAL_CONDITIONS,
              "percent", "ICE BofA BBB US Corporate OAS"),
    SeriesDef("NFCI", "Chicago Fed NFCI", Source.FRED, Frequency.WEEKLY, Theme.FINANCIAL_CONDITIONS,
              "index", "Chicago Fed National Financial Conditions Index"),
    SeriesDef("STLFSI2", "StL Fed Financial Stress", Source.FRED, Frequency.WEEKLY, Theme.FINANCIAL_CONDITIONS,
              "index", "St. Louis Fed Financial Stress Index"),
    SeriesDef("VIXCLS", "CBOE VIX", Source.FRED, Frequency.DAILY, Theme.FINANCIAL_CONDITIONS,
              "index", "CBOE Volatility Index: VIX"),
    SeriesDef("TEDRATE", "TED Spread", Source.FRED, Frequency.DAILY, Theme.FINANCIAL_CONDITIONS,
              "percent", "TED Rate"),

    # ── Growth & Activity (5) ──────────────────────────────────────────
    SeriesDef("GDP", "Nominal GDP", Source.FRED, Frequency.QUARTERLY, Theme.GROWTH,
              "billions", "Gross Domestic Product"),
    SeriesDef("GDPC1", "Real GDP", Source.FRED, Frequency.QUARTERLY, Theme.GROWTH,
              "billions", "Real Gross Domestic Product"),
    SeriesDef("INDPRO", "Industrial Production", Source.FRED, Frequency.MONTHLY, Theme.GROWTH,
              "index", "Industrial Production: Total Index"),
    SeriesDef("RSAFS", "Retail Sales", Source.FRED, Frequency.MONTHLY, Theme.GROWTH,
              "millions", "Advance Retail Sales: Retail and Food Services, Total"),
    SeriesDef("NAPM", "ISM Manufacturing PMI", Source.FRED, Frequency.MONTHLY, Theme.GROWTH,
              "index", "ISM Manufacturing: PMI Composite Index"),

    # ── FX & Market (4, via yfinance) ──────────────────────────────────
    SeriesDef("DX-Y.NYB", "US Dollar Index (DXY)", Source.YFINANCE, Frequency.DAILY, Theme.FX_MARKET,
              "index", "ICE US Dollar Index"),
    SeriesDef("EURUSD=X", "EUR/USD", Source.YFINANCE, Frequency.DAILY, Theme.FX_MARKET,
              "rate", "Euro to US Dollar exchange rate"),
    SeriesDef("JPY=X", "USD/JPY", Source.YFINANCE, Frequency.DAILY, Theme.FX_MARKET,
              "rate", "US Dollar to Japanese Yen exchange rate"),
    SeriesDef("^GSPC", "S&P 500", Source.YFINANCE, Frequency.DAILY, Theme.FX_MARKET,
              "index", "S&P 500 Index"),
]

# ── Lookup Helpers ──────────────────────────────────────────────────────────

SERIES_MAP: dict[str, SeriesDef] = {s.series_id: s for s in SERIES_CATALOG}


def get_series(series_id: str) -> SeriesDef | None:
    return SERIES_MAP.get(series_id)


def get_series_by_source(source: Source) -> list[SeriesDef]:
    return [s for s in SERIES_CATALOG if s.source == source]


def get_series_by_theme(theme: Theme) -> list[SeriesDef]:
    return [s for s in SERIES_CATALOG if s.theme == theme]
