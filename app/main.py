from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.db.database import engine, Base
from app.db import models
from app.routers import auth, dashboard, customers, reports

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

# Static files mounten
# Check if app/static exists
import os
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(reports.router)

@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/login")
