"""Source registry for data ingestors."""

from .fred import FredIngestor
from .yfinance import YFinanceIngestor
from .oecd import OecdIngestor
from .worldbank import WorldBankIngestor
from .bls import BlsIngestor

REGISTRY = {
    "fred": FredIngestor,
    "yfinance": YFinanceIngestor,
    "oecd": OecdIngestor,
    "worldbank": WorldBankIngestor,
    "bls": BlsIngestor,
}
