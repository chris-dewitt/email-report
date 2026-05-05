import json
from pathlib import Path

import pytest

from balancelab.models.positions import BalanceSheet

SAMPLE_DATA = Path(__file__).parent.parent / "sample_data" / "sample_balance_sheet.json"


@pytest.fixture
def sample_bs() -> BalanceSheet:
    data = json.loads(SAMPLE_DATA.read_text(encoding="utf-8"))
    return BalanceSheet.model_validate(data)


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    for sub in ("bronze", "silver", "gold"):
        (tmp_path / sub).mkdir()
    return tmp_path
