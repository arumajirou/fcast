from __future__ import annotations
from typing import Any, Iterable
from sqlalchemy.orm import Session

def upsert_one(session: Session, model, keys: dict[str, Any], values: dict[str, Any]):
    obj = session.query(model).filter_by(**keys).one_or_none()
    if obj is None:
        obj = model(**{**keys, **values})
        session.add(obj)
        session.flush()
    else:
        for k, v in values.items():
            setattr(obj, k, v)
        session.flush()
    return obj

def to_df(rows: Iterable[Any], columns: list[str]):
    import pandas as pd
    return pd.DataFrame([{c: getattr(r, c) for c in columns} for r in rows])
