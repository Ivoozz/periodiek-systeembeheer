import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
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
    # Persistent connection for StaticPool to avoid re-opening/decrypting on every request
    conn = pysqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(f"PRAGMA key = '{DATABASE_KEY}'")
    # PERFORMANCE: Optimize SQLite for LXC
    conn.execute("PRAGMA journal_mode=WAL") # Use WAL for better concurrency
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000") # 64MB Cache
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn

# PERFORMANCE: Use a small pool to balance decryption overhead and concurrency
engine = create_engine(
    "sqlite://", 
    creator=get_connection,
    connect_args={"check_same_thread": False},
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
