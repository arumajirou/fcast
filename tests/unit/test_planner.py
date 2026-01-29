from fcast.meta.db import session_scope, init_db
from fcast.pipeline.planner import ensure_7_selectors_loto6
from fcast.meta.orm import ModelsSeriesSelector

def test_ensure_7_selectors(engine, monkeypatch):
    # engine fixture sets env and creates tables
    selectors = ensure_7_selectors_loto6()
    assert len(selectors) == 7
