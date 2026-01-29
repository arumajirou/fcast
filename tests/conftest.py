import os
import sys
import tempfile
from pathlib import Path

# Ensure src-layout imports work without installation
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest
from sqlalchemy import create_engine
from fcast.meta.orm import Base

@pytest.fixture(scope="session")
def temp_meta_db_url():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return f"sqlite:///{path}"

@pytest.fixture()
def engine(temp_meta_db_url, monkeypatch):
    monkeypatch.setenv("FCAST_META_URL", temp_meta_db_url)
    eng = create_engine(temp_meta_db_url, future=True)
    Base.metadata.create_all(bind=eng)
    return eng
