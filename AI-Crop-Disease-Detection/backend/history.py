"""
history.py
==========
SQLAlchemy-based prediction history storage using SQLite.
Saves each prediction result for later retrieval via GET /history.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_URL   = f"sqlite:///{BASE_DIR / 'database.db'}"

# ── Database Setup ────────────────────────────────────────────────────────────
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class PredictionRecord(Base):
    """ORM model for a single prediction entry."""
    __tablename__ = "predictions"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename   = Column(String, nullable=False)
    disease    = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    timestamp  = Column(DateTime, default=datetime.utcnow, nullable=False)


def init_db() -> None:
    """Create tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)
    log.info(f"✅ Database initialised at {BASE_DIR / 'database.db'}")


def get_db() -> Session:
    """Dependency injection helper for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_prediction(
    db: Session,
    filename: str,
    disease: str,
    confidence: float,
) -> PredictionRecord:
    """
    Persist a prediction record to SQLite.

    Args:
        db:         SQLAlchemy Session (injected by FastAPI dependency).
        filename:   Original uploaded filename.
        disease:    Predicted disease class name.
        confidence: Model confidence score (0–1).

    Returns:
        The created PredictionRecord.
    """
    record = PredictionRecord(
        filename=filename,
        disease=disease,
        confidence=round(confidence, 4),
        timestamp=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    log.info(f"Prediction saved: {disease} ({confidence:.2%}) — file: {filename}")
    return record


def get_prediction_history(
    db: Session,
    limit: int = 50,
    offset: int = 0,
) -> List[PredictionRecord]:
    """
    Retrieve the most recent predictions in reverse chronological order.
    """
    return (
        db.query(PredictionRecord)
        .order_by(PredictionRecord.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
