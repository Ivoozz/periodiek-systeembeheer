import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = "/var/www/systeembeheer/data.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

engine = create_engine("sqlite:///" + DB_PATH)
Base = declarative_base()

class TestTable(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True)
    name = Column(String)

print(f"Creating database at {DB_PATH}...")
try:
    Base.metadata.create_all(engine)
    print("Success: Database created without special SQLCipher pragmas.")
except Exception as e:
    print(f"Failed: {e}")
