from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import auth, models

router = APIRouter(prefix="/admin/v2", tags=["web-dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_v2(
    request: Request, 
    user: models.User = Depends(auth.require_behandelaar),
    db: Session = Depends(get_db)
):
    # Fetch real counts from DB where available
    active_customers_count = db.query(models.User).filter(models.User.role == "Klant").count()
    completed_reports_count = db.query(models.Report).count()
    
    # Mock some data for the prototype components that don't have full DB backing yet
    stats = {
        "active_customers": active_customers_count,
        "pending_reports": 2, # Mock: concept rapportages
        "completed_checks": completed_reports_count,
        "system_health": "99.9%"
    }
    
    return templates.TemplateResponse("admin/dashboard_v2.html", {
        "request": request, 
        "user": user,
        "stats": stats
    })
