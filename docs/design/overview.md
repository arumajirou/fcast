# Design overview

- Postgres(or SQLite for dev): forecast_meta
- Lakehouse (Parquet for dev): forecast_lake
- Plugins: src/fcast/plugins
- Pipeline: src/fcast/pipeline (planner -> validator -> runner)
