import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data.db"))
DATABASE_KEY = os.getenv("DATABASE_KEY", "change_me_in_production")

# Ensure the directory for the database exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

import pysqlite3

def get_connection():
    # Production-ready connection with SQLCipher key
    conn = pysqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(f"PRAGMA key = '{DATABASE_KEY}'")
    # PERFORMANCE: Enable WAL for better concurrency in multi-user SaaS
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000") 
    return conn

# PERFORMANCE: Use QueuePool for robust concurrent access
engine = create_engine(
    "sqlite://", 
    creator=get_connection,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
