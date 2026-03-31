from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Customer, Report, ReportStatus
from app.core.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    customer_count = db.query(Customer).count()
    report_count = db.query(Report).count()
    recent_reports = db.query(Report).order_by(Report.date_performed.desc()).limit(5).all()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "customer_count": customer_count,
            "report_count": report_count,
            "recent_reports": recent_reports,
            "user": current_user
        }
    )
