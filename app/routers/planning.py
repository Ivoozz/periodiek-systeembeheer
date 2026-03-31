from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Role, Customer, Assignment, AssignmentStatus
from app.core.auth import require_admin
from fastapi.templating import Jinja2Templates
from datetime import datetime

router = APIRouter(prefix="/admin/planning", tags=["planning"], dependencies=[Depends(require_admin)])

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def get_planning(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    assignments = db.query(Assignment).order_by(Assignment.scheduled_date.asc()).all()
    technicians = db.query(User).filter(User.role == Role.TECHNICUS).all()
    customers = db.query(Customer).all()
    
    # Unplanned customers: customers without any PLANNED assignment
    planned_customer_ids = [a.customer_id for a in assignments if a.status == AssignmentStatus.PLANNED]
    unplanned_customers = db.query(Customer).filter(~Customer.id.in_(planned_customer_ids)).all()
    
    return templates.TemplateResponse("admin/planning.html", {
        "request": request,
        "assignments": assignments,
        "technicians": technicians,
        "customers": customers,
        "unplanned_customers": unplanned_customers,
        "user": current_user
    })

@router.post("/assign")
async def assign_assignment(
    request: Request,
    customer_id: int = Form(...),
    technician_id: int = Form(...),
    scheduled_date: str = Form(...),
    is_recurring: bool = Form(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    try:
        # Support both date and datetime formats
        if len(scheduled_date) == 10:
            dt = datetime.strptime(scheduled_date, '%Y-%m-%d')
        else:
            dt = datetime.fromisoformat(scheduled_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ongeldige datum of tijd formaat")
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    interval = customer.interval_days if customer else 30

    assignment = Assignment(
        customer_id=customer_id,
        technician_id=technician_id,
        scheduled_date=dt,
        status=AssignmentStatus.PLANNED,
        is_recurring=is_recurring,
        interval_days=interval
    )
    db.add(assignment)
    db.commit()
    
    return RedirectResponse(url="/admin/planning", status_code=303)
