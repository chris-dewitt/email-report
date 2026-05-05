from balancelab.config import ALL_DIRS, DATA_DIR


def ensure_data_dirs() -> None:
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "balance_sheets").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "scenarios").mkdir(parents=True, exist_ok=True)
