from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
from app.db.session import SessionLocal

Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
