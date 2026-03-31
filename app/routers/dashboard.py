from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Customer, Report, Role, Assignment
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
    customer_count = 0
    report_count = 0
    recent_reports = []
    upcoming_assignments = []
    
    if current_user.role == Role.ADMIN:
        customer_count = db.query(Customer).count()
        report_count = db.query(Report).count()
        recent_reports = db.query(Report).order_by(Report.date_performed.desc()).limit(5).all()
        upcoming_assignments = db.query(Assignment).order_by(Assignment.scheduled_date).limit(5).all()
        
    elif current_user.role == Role.TECHNICUS:
        # Technicians only see their own assignments and reports
        customer_count = db.query(Customer).join(Assignment).filter(Assignment.technician_id == current_user.id).distinct().count()
        report_count = db.query(Report).filter(Report.technician_id == current_user.id).count()
        recent_reports = db.query(Report).filter(Report.technician_id == current_user.id).order_by(Report.date_performed.desc()).limit(5).all()
        upcoming_assignments = db.query(Assignment).filter(Assignment.technician_id == current_user.id).order_by(Assignment.scheduled_date).limit(5).all()

    elif current_user.role == Role.CLIENT:
        # Clients only see their own company's data
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if not customer:
            # Fallback if no customer is linked yet
            return templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "user": current_user, "no_customer": True}
            )
        
        customer_count = 1
        report_count = db.query(Report).filter(Report.customer_id == customer.id).count()
        recent_reports = db.query(Report).filter(Report.customer_id == customer.id).order_by(Report.date_performed.desc()).limit(5).all()
        upcoming_assignments = db.query(Assignment).filter(Assignment.customer_id == customer.id).order_by(Assignment.scheduled_date).limit(5).all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "customer_count": customer_count,
            "report_count": report_count,
            "recent_reports": recent_reports,
            "upcoming_assignments": upcoming_assignments,
            "user": current_user
        }
    )
