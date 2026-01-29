from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
import pandas as pd

@dataclass
class Violation:
    code: str
    message: str
    severity: str = "error"

def validate_long_df(df: pd.DataFrame, id_col="unique_id", time_col="ds", target_col="y") -> list[Violation]:
    v: list[Violation] = []
    for c in [id_col, time_col, target_col]:
        if c not in df.columns:
            v.append(Violation(code="missing_column", message=f"Missing column: {c}"))
    if v:
        return v
    if df[id_col].isna().any():
        v.append(Violation(code="null_id", message="unique_id contains null"))
    if df[target_col].isna().any():
        v.append(Violation(code="null_y", message="y contains null"))
    # simple monotonic check per series
    for uid, g in df.sort_values([id_col, time_col]).groupby(id_col):
        if not g[time_col].is_monotonic_increasing:
            v.append(Violation(code="time_not_sorted", message=f"{uid}: ds not sorted"))
            break
    return v

def validate_feature_prefixes(df: pd.DataFrame) -> list[Violation]:
    # ensure feature columns follow hist_/stat_/fut_ prefixes if present
    v: list[Violation] = []
    feature_cols = [c for c in df.columns if c not in ("unique_id","ds","y")]
    for c in feature_cols:
        if not (c.startswith("hist_") or c.startswith("stat_") or c.startswith("fut_") or c.startswith("anom_")):
            v.append(Violation(code="bad_prefix", message=f"Feature column missing prefix: {c}", severity="warn"))
    return v
