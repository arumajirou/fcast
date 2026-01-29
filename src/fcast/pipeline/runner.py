from __future__ import annotations
import time
from datetime import datetime
import pandas as pd
from fcast.meta.db import session_scope
from fcast.meta.orm import (
    RunsPlan, RunsStep, RunsParam, RunsValidation, RunsResult, RunsMetric, RunsArtifact,
)
from fcast.lake.paths import table_path
from fcast.lake.io import write_parquet
from fcast.pipeline.validator import validate_long_df, validate_feature_prefixes

def mock_run_plan(run_id: str, df: pd.DataFrame, preds_h: int = 5) -> None:
    # Minimal example: validate -> "predict" -> metrics
    violations = validate_long_df(df) + validate_feature_prefixes(df)
    ok = all(v.severity != "error" for v in violations)

    with session_scope() as s:
        steps = s.query(RunsStep).filter_by(run_id=run_id).order_by(RunsStep.ord).all()
        for st in steps:
            s.add(RunsValidation(run_step_id=st.run_step_id, ok=ok,
                                violations=[v.__dict__ for v in violations]))
            s.add(RunsResult(run_step_id=st.run_step_id, status="success" if ok else "failed",
                             started_at=datetime.utcnow(), ended_at=datetime.utcnow(), summary={}))
        s.flush()

    if not ok:
        return

    # mock predictions: y_hat = last_y
    df2 = df.sort_values(["unique_id","ds"])
    last = df2.groupby("unique_id").tail(1)[["unique_id","ds","y"]].copy()
    preds = []
    for i in range(1, preds_h+1):
        tmp = last.copy()
        tmp["ds"] = pd.to_datetime(tmp["ds"]) + pd.to_timedelta(i, unit="W")
        tmp["y_hat"] = tmp["y"]
        preds.append(tmp[["unique_id","ds","y_hat"]])
    pred_df = pd.concat(preds, ignore_index=True)
    out_path = table_path("gold", f"predictions_{run_id}")
    write_parquet(pred_df, out_path)

    # store artifact + a dummy metric
    with session_scope() as s:
        s.add(RunsArtifact(run_id=run_id, artifact_type="predictions", storage_uri=str(out_path), meta={"h": preds_h}))
        # dummy metric: variance of y
        metric = float(df["y"].var()) if len(df) > 1 else 0.0
        # attach to first step (ord=0)
        first_step = s.query(RunsStep).filter_by(run_id=run_id).order_by(RunsStep.ord).first()
        if first_step:
            s.add(RunsMetric(run_step_id=first_step.run_step_id, metric_name="y_var", metric_value=metric, split_tag="train"))
