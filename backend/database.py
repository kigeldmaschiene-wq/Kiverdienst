"""Database configuration and session management for KIVerdienst v2 backend."""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


logger = logging.getLogger(__name__)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://kiverdienst:secure123kiverdienst@postgres:5432/kiverdienst_v2",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
Base = declarative_base()


def get_db() -> Generator:
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator:
    """Provide a transactional scope for scripts or background tasks."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception("Database session rollback due to error: %s", exc)
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create database tables if they do not already exist."""
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
