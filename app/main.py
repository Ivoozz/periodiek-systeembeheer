from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import engine, Base, get_db
from app.models import SystemSettings
from app.routers import auth, users, reports, external, settings
import os

# Database tables aanmaken
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Periodiek Systeembeheer")

# Static files & Templates
os.makedirs("app/static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Context processor voor globale instellingen (logo, header, footer)
@app.middleware("http")
async def add_settings_to_context(request: Request, call_next):
    # Dit is lastig in middleware voor Jinja2, we doen het via een dependency of direct in de routes
    response = await call_next(request)
    return response

def get_system_settings(db: Session):
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings(header_text="Periodiek Systeembeheer", footer_text="© 2026 Systeembeheer")
    return settings

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reports.router)
app.include_router(external.router)
app.include_router(settings.router)

@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    # Check if logged in via cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    
    # Simpele redirect naar dashboard op basis van rol (zou via auth moeten, maar dit is de root)
    return RedirectResponse(url="/dashboard")

# Voor de frontend routes
@app.get("/login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    settings = get_system_settings(db)
    return templates.TemplateResponse("login.html", {"request": request, "settings": settings})

@app.get("/dashboard")
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    # Dashboard route logic (admin of klant)
    settings = get_system_settings(db)
    # Normaal gesproken checken we hier de rol via auth
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "settings": settings})

@app.get("/admin/instellingen")
async def settings_page(request: Request, db: Session = Depends(get_db)):
    settings = get_system_settings(db)
    return templates.TemplateResponse("admin/settings.html", {"request": request, "settings": settings})
