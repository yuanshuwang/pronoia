from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.models.base import Base
from utils.config import get_nested, load_settings

_engine = None
_session_factory: sessionmaker[Session] | None = None


def get_engine():
    global _engine
    if _engine is None:
        settings = load_settings()
        _engine = create_engine(
            settings["database_url"],
            pool_size=get_nested(settings, "database", "pool_size", default=5),
            max_overflow=get_nested(settings, "database", "max_overflow", default=5),
            echo=get_nested(settings, "database", "echo", default=False),
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _session_factory


def init_db() -> None:
    import database.models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
