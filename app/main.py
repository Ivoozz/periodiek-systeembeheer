from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import engine, Base
from app.db import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Periodiek Systeembeheer",
    description="Modern monolith for periodic system maintenance reports",
    version="3.5",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Welcome to Periodiek Systeembeheer API"}
