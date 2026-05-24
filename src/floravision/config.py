from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
DEFAULT_CATALOG_PATH = DATA_DIR / "flora_catalog.json"
DEFAULT_DB_PATH = DATA_DIR / "floravision.sqlite3"


def _float_from_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = "FloraVision AI"
    catalog_path: Path = DEFAULT_CATALOG_PATH
    db_path: Path = Path(os.getenv("FLORAVISION_DB_PATH", str(DEFAULT_DB_PATH)))
    model_id: str = os.getenv("FLORAVISION_MODEL_ID", "openai/clip-vit-base-patch32")
    confidence_threshold: float = _float_from_env("FLORAVISION_CONFIDENCE_THRESHOLD", 0.17)


def get_settings() -> Settings:
    return Settings()

