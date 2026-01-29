from __future__ import annotations
from typing import Sequence
from fcast.meta.orm import ModelsSeriesSelector
from fcast.meta.db import session_scope

def ensure_7_selectors_loto6() -> list[ModelsSeriesSelector]:
    # N1..N6 + ALL
    selectors: list[ModelsSeriesSelector] = []
    with session_scope() as s:
        for i in range(1, 7):
            name = f"loto6_N{i}"
            obj = s.query(ModelsSeriesSelector).filter_by(name=name).one_or_none()
            if obj is None:
                obj = ModelsSeriesSelector(name=name, game_code="loto6", unique_id_list=[f"N{i}"])
                s.add(obj)
            selectors.append(obj)
        all_name = "loto6_ALL"
        all_obj = s.query(ModelsSeriesSelector).filter_by(name=all_name).one_or_none()
        if all_obj is None:
            all_obj = ModelsSeriesSelector(name=all_name, game_code="loto6", unique_id_list=[f"N{i}" for i in range(1,7)])
            s.add(all_obj)
        selectors.append(all_obj)
        s.flush()
    return selectors
