from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging
from dotenv import load_dotenv

# Laad .env indien aanwezig
load_dotenv()

logger = logging.getLogger(__name__)

# Absoluut pad voor productie uniformiteit
DATABASE_URL = "sqlite:////var/www/systeembeheer/systeembeheer.db"
DATABASE_KEY = os.getenv("DATABASE_KEY")

# We proberen pysqlite3 te laden voor SQLCipher ondersteuning op Python 3.13
try:
    from pysqlite3 import dbapi2 as sqlite
    logger.info("pysqlite3-binary succesvol geladen.")
except ImportError:
    import sqlite3 as sqlite
    logger.info("Standaard sqlite3 module geladen.")

engine = create_engine(DATABASE_URL, module=sqlite)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    if DATABASE_KEY:
        try:
            # SQLCipher PRAGMA key instellen
            cursor.execute(f"PRAGMA key = '{DATABASE_KEY}'")
            # Test of de encryptie werkt door een simpele query
            cursor.execute("SELECT count(*) FROM sqlite_master")
            logger.info("SQLCipher encryptie succesvol geactiveerd.")
        except Exception as e:
            logger.error(f"FOUT: Kon SQLCipher key niet toepassen of driver ondersteunt geen encryptie: {e}")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
