from __future__ import annotations
import pandas as pd

def add_basic_transforms(df: pd.DataFrame, y_col: str = "y", windows=(3,7)) -> pd.DataFrame:
    # expects columns: unique_id, ds, y
    out = df.copy()
    out = out.sort_values(["unique_id", "ds"])
    g = out.groupby("unique_id", group_keys=False)

    out["hist_y_diff1"] = g[y_col].diff(1)
    out["hist_y_cumsum"] = g[y_col].cumsum()

    for w in windows:
        out[f"hist_y_roll_sum_{w}"] = g[y_col].rolling(w).sum().reset_index(level=0, drop=True)
        out[f"hist_y_roll_mean_{w}"] = g[y_col].rolling(w).mean().reset_index(level=0, drop=True)
    return out
