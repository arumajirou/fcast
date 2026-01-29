from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    meta_url: str = "sqlite:///./forecast_meta.db"
    lake_dir: str = "./forecast_lake"
    reports_dir: str = "./reports"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_prefix="FCAST_", env_file=".env", extra="ignore")

settings = Settings()
