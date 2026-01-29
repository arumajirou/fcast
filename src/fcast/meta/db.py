from __future__ import annotations
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fcast.config import settings
from fcast.meta.orm import Base

def get_engine():
    url = os.getenv("FCAST_META_URL", settings.meta_url)
    return create_engine(url, future=True)

def get_sessionmaker():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)

@contextmanager
def session_scope() -> Session:
    SessionLocal = get_sessionmaker()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
