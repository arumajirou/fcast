from __future__ import annotations
from pathlib import Path
from fcast.config import settings

def lake_root() -> Path:
    return Path(settings.lake_dir).resolve()

def ensure_dirs():
    root = lake_root()
    for p in [root / "bronze", root / "silver", root / "gold"]:
        p.mkdir(parents=True, exist_ok=True)
    return root

def table_path(layer: str, name: str) -> Path:
    root = ensure_dirs()
    return root / layer / f"{name}.parquet"
