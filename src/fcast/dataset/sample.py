from __future__ import annotations
import numpy as np
import pandas as pd

def make_sample_loto(game_code: str = "loto6", n_draws: int = 200, seed: int = 7):
    # NOTE: This is synthetic data for pipeline validation, not real lottery scraping.
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2020-01-01")
    dates = pd.date_range(start, periods=n_draws, freq="W")  # weekly draws
    if game_code == "numbers3":
        k = 3
        maxv = 9
    elif game_code == "numbers4":
        k = 4
        maxv = 9
    elif game_code == "miniloto":
        k = 5
        maxv = 31
    elif game_code == "loto6":
        k = 6
        maxv = 43
    elif game_code == "loto7":
        k = 7
        maxv = 37
    elif game_code == "bingo5":
        k = 5
        maxv = 39
    else:
        # fallback
        k = 6
        maxv = 50

    # For demonstration: generate k "slots" with slightly different distributions
    wide = pd.DataFrame({"ds": dates})
    for i in range(1, k+1):
        # slight drift per slot to make columns non-identical
        vals = rng.integers(1, maxv+1, size=n_draws) + (i % 3)
        vals = np.clip(vals, 1, maxv)
        wide[f"N{i}"] = vals
    return wide

def wide_to_long(wide: pd.DataFrame, k: int) -> pd.DataFrame:
    long_rows = []
    for i in range(1, k+1):
        tmp = wide[["ds", f"N{i}"]].copy()
        tmp["unique_id"] = f"N{i}"
        tmp = tmp.rename(columns={f"N{i}":"y"})
        long_rows.append(tmp)
    long = pd.concat(long_rows, ignore_index=True)
    return long[["unique_id","ds","y"]]
