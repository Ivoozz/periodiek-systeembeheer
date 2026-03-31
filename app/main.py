from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
import os

from app.db.database import engine, Base, get_db
from app.db import models
from app.routers import auth, dashboard, customers, reports, api, technician, planning, settings
from app.core import branding
from app.core.templates import templates
from app.core.auth import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Periodiek Systeembeheer",
    description="Modern monolith for periodic system maintenance reports",
    version="4.5.1",
    lifespan=lifespan
)

# CLOUDFLARE / REVERSE PROXY SUPPORT
# Trust proxy headers (X-Forwarded-For, X-Forwarded-Proto)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        if request.headers.get("HX-Request"):
            response = HTMLResponse("")
            response.headers["HX-Redirect"] = "/login"
            return response
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    db = next(get_db())
    brand_settings = branding.get_branding_settings(db)

    return templates.TemplateResponse(
        "error.html", 
        {
            "request": request, 
            "status_code": exc.status_code, 
            "message": exc.detail or "Er is iets misgegaan",
            "branding": brand_settings
        }, 
        status_code=exc.status_code
    )

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Content Security Policy (Optimized for Cloudflare and Performance)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
        "img-src 'self' data: *; "
        "connect-src 'self' *;"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Static files mounten
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(reports.router)
app.include_router(api.router)
app.include_router(technician.router)
app.include_router(planning.router)
app.include_router(settings.router)

@app.get("/")
async def root(request: Request, user: models.User = Depends(get_current_user)):
    if user:
        if user.role == models.Role.TECHNICUS:
            return RedirectResponse(url="/behandelaar/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
