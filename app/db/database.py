import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data.db"))
DATABASE_KEY = os.getenv("DATABASE_KEY", "change_me_in_production")

# Ensure the directory for the database exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Using pysqlite3-binary for SQLCipher support
import pysqlite3

def get_connection():
    # Simple connection without WAL to avoid I/O issues on some LXC storage backends
    conn = pysqlite3.connect(DB_PATH, check_same_thread=False)
    # Set key immediately on raw connection
    conn.execute(f"PRAGMA key = '{DATABASE_KEY}'")
    return conn

engine = create_engine(
    "sqlite://", 
    creator=get_connection,
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # Explicitly use DELETE mode instead of WAL to maximize compatibility
    cursor.execute("PRAGMA journal_mode=DELETE")
    cursor.execute("PRAGMA synchronous=FULL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
