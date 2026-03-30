from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import os
import logging
import hashlib

from app.db.session import engine, Base, get_db
from app.models import SystemSettings, User
from app.routers import users, reports, settings, customers, auth
from app.core.auth import get_current_user, require_behandelaar
from app.api.v1 import external
from app.web import dashboard

# Dynamische padbepaling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logging instellen
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_system_settings(db: Session):
    try:
        settings = db.query(SystemSettings).first()
        if not settings:
            settings = SystemSettings(header_text="Periodiek Systeembeheer", footer_text="© 2026 Systeembeheer")
        return settings
    except Exception as e:
        logger.error(f"Fout bij ophalen instellingen: {e}")
        return SystemSettings(header_text="Systeembeheer", footer_text="© 2026")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Applicatie start op...")
    try:
        os.makedirs(os.path.join(BASE_DIR, "app/static/uploads"), exist_ok=True)
    except Exception as e:
        logger.error(f"Fout bij aanmaken mappen: {e}")

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tabellen gecontroleerd.")
    except Exception as e:
        logger.error(f"CRITIEKE FOUT bij database initialisatie: {e}")
    
    yield
    logger.info("Applicatie sluit af...")

app = FastAPI(title="Periodiek Systeembeheer", lifespan=lifespan)

# Static files mounten
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app/static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app/templates"))

# CACHEBUSTER LOGICA
def get_static_hash(path: str):
    """Berekent een MD5 hash van een statisch bestand voor cache-busting."""
    full_path = os.path.join(BASE_DIR, "app/static", path.lstrip("/"))
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    return "1"

def hashed_static_url(path: str):
    """Genereert een URL met een v= query parameter gebaseerd op de bestandsinhoud."""
    v = get_static_hash(path)
    return f"/static/{path.lstrip('/')}?v={v}"

# Voeg de helper toe aan Jinja2 templates
templates.env.globals["static_url"] = hashed_static_url

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reports.router)
app.include_router(external.router)
app.include_router(settings.router)
app.include_router(customers.router)
app.include_router(dashboard.router)

@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/dashboard")

@app.get("/login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    settings = get_system_settings(db)
    return templates.TemplateResponse("login.html", {"request": request, "settings": settings})

@app.get("/dashboard")
async def dashboard_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    settings = get_system_settings(db)
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "settings": settings, "user": current_user})

@app.get("/admin/instellingen")
async def settings_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_behandelaar)):
    settings = get_system_settings(db)
    return templates.TemplateResponse("admin/settings.html", {"request": request, "settings": settings, "user": current_user})
