from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
import datetime
from sqlalchemy.sql import func
from app.db.models import Customer, Report, Role, Assignment

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
    
    # Maintenance Volume Chart Data (Last 6 Months)
    maintenance_data = []
    maintenance_labels = []
    for i in range(5, -1, -1):
        month_start = datetime.datetime.now() - datetime.timedelta(days=i*30)
        month_name = month_start.strftime("%b")
        maintenance_labels.append(month_name)
        
        # Count reports for this month
        start_date = month_start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
            
        count = db.query(Report).filter(Report.date_performed >= start_date, Report.date_performed < end_date)
        if current_user.role == Role.TECHNICUS:
            count = count.filter(Report.technician_id == current_user.id)
        elif current_user.role == Role.CLIENT:
            customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
            if customer:
                count = count.filter(Report.customer_id == customer.id)
        
        maintenance_data.append(count.count())

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
            "maintenance_labels": maintenance_labels,
            "maintenance_data": maintenance_data,
            "now": datetime.datetime.now(),
            "timedelta": datetime.timedelta,
            "user": current_user
        }
    )

@router.get("/dashboard/assignments", response_class=HTMLResponse)
async def dashboard_assignments(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_required)
):
    upcoming_assignments = []
    if current_user.role == Role.ADMIN:
        upcoming_assignments = db.query(Assignment).order_by(Assignment.scheduled_date).limit(5).all()
    elif current_user.role == Role.TECHNICUS:
        upcoming_assignments = db.query(Assignment).filter(Assignment.technician_id == current_user.id).order_by(Assignment.scheduled_date).limit(5).all()
    elif current_user.role == Role.CLIENT:
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if customer:
            upcoming_assignments = db.query(Assignment).filter(Assignment.customer_id == customer.id).order_by(Assignment.scheduled_date).limit(5).all()

    return templates.TemplateResponse(
        "dashboard_assignments.html",
        {
            "request": request,
            "upcoming_assignments": upcoming_assignments,
            "now": datetime.datetime.now(),
            "timedelta": datetime.timedelta
        }
    )
