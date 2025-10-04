from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db as _get_db


def get_db() -> Session:
    # FastAPI dependency wrapper for DB session
    for db in _get_db():
        return db
