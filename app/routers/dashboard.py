from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Customer, Report, ReportStatus, Role, Assignment, AssignmentStatus
from app.core.auth import get_current_user_required
from app.core.templates import templates

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_required)
):
    # Base queries
    customer_count_query = db.query(Customer)
    report_count_query = db.query(Report)
    recent_reports_query = db.query(Report)
    
    # Filter based on role
    if current_user.role != Role.ADMIN:
        # Technicians only see their own data
        report_count_query = report_count_query.filter(Report.technician_id == current_user.id)
        recent_reports_query = recent_reports_query.filter(Report.technician_id == current_user.id)
        
        # Only count customers they have assignments for? 
        # For simplicity, we'll keep the customer count global or for those they are assigned to.
        # But for "Ultra Visual", let's make it specific to the tech.
        customer_count = db.query(Customer).join(Assignment).filter(Assignment.technician_id == current_user.id).distinct().count()
    else:
        customer_count = customer_count_query.count()

    report_count = report_count_query.count()
    recent_reports = recent_reports_query.order_by(Report.date_performed.desc()).limit(5).all()
    
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
