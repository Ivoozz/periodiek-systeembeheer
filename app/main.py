from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import os
import logging

from app.db.session import engine, Base, get_db
from app.models import SystemSettings
from app.routers import auth, users, reports, external, settings

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
    # Startup logica
    logger.info("Applicatie start op...")
    
    # Mappen aanmaken
    try:
        os.makedirs("/var/www/systeembeheer/app/static/uploads", exist_ok=True)
        logger.info("Upload mappen gecontroleerd.")
    except Exception as e:
        logger.error(f"Fout bij aanmaken mappen: {e}")

    # Database initialisatie (verplaatst van module-niveau naar hier)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tabellen gecontroleerd/aangemaakt.")
    except Exception as e:
        logger.error(f"CRITIEKE FOUT bij database initialisatie: {e}")
        # We laten de app wel doorstarten zodat de gateway niet doodslaat, 
        # maar API calls zullen falen met duidelijke logs.
    
    yield
    # Shutdown logica indien nodig
    logger.info("Applicatie sluit af...")

app = FastAPI(title="Periodiek Systeembeheer", lifespan=lifespan)

# Static files & Templates
app.mount("/static", StaticFiles(directory="/var/www/systeembeheer/app/static"), name="static")
templates = Jinja2Templates(directory="/var/www/systeembeheer/app/templates")

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reports.router)
app.include_router(external.router)
app.include_router(settings.router)

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
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    settings = get_system_settings(db)
    # De specifieke dashboard logica (admin/klant) wordt in de frontend/router afgehandeld
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "settings": settings})

@app.get("/admin/instellingen")
async def settings_page(request: Request, db: Session = Depends(get_db)):
    settings = get_system_settings(db)
    return templates.TemplateResponse("admin/settings.html", {"request": request, "settings": settings})
