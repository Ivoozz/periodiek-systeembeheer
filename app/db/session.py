from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Laad .env indien aanwezig
load_dotenv()

# Absoluut pad voor productie uniformiteit
DATABASE_URL = "sqlite:////var/www/systeembeheer/systeembeheer.db"
DATABASE_KEY = os.getenv("DATABASE_KEY")

try:
    from pysqlite3 import dbapi2 as sqlite
except ImportError:
    import sqlite3 as sqlite

engine = create_engine(DATABASE_URL, module=sqlite)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    if DATABASE_KEY:
        cursor.execute(f"PRAGMA key = '{DATABASE_KEY}'")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
