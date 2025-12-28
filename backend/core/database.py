from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator
import structlog
import os

from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


def get_database_url() -> str:
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    
    if settings.USE_SQLITE:
        db_path = settings.SQLITE_DB_PATH
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        sqlite_url = f"sqlite:///{db_path}"
        logger.info("Using SQLite database", path=db_path)
        return sqlite_url
    
    raise ValueError("DATABASE_URL not set and USE_SQLITE is False")


database_url = get_database_url()

if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if database_url.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    logger.debug("Database connection established")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    return SessionLocal()

