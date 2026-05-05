from balancelab.settings import settings

DATA_DIR = settings.data_dir
DUCKDB_PATH = DATA_DIR / settings.duckdb_path

BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

ALL_DIRS = [BRONZE_DIR, SILVER_DIR, GOLD_DIR]
