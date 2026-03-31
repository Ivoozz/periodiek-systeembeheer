from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Assignment, AssignmentStatus, Customer
from app.core.auth import require_technician

router = APIRouter(prefix="/behandelaar", tags=["technician"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def technician_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technician)
):
    assignments = db.query(Assignment).join(Customer).filter(
        Assignment.technician_id == current_user.id,
        Assignment.status == AssignmentStatus.PLANNED
    ).all()
    
    return templates.TemplateResponse(
        "technician/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "assignments": assignments
        }
    )
