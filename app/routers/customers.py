from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from app.db.database import get_db
from app.db.models import Customer, User
from app.core.auth import require_admin
from app.core.templates import templates

router = APIRouter(prefix="/customers", tags=["customers"], dependencies=[Depends(require_admin)])

@router.get("/", response_class=HTMLResponse)
async def list_customers(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
    search: Optional[str] = None
):
    query = db.query(Customer)
    if search:
        query = query.filter(Customer.name.contains(search))
    customers = query.order_by(Customer.name).all()
    return templates.TemplateResponse(
        "customers.html",
        {"request": request, "customers": customers, "user": user, "search": search}
    )

@router.get("/table", response_class=HTMLResponse)
async def get_customers_table(
    request: Request,
    db: Session = Depends(get_db),
    search: Optional[str] = None
):
    query = db.query(Customer)
    if search:
        query = query.filter(Customer.name.contains(search))
    customers = query.order_by(Customer.name).all()
    return templates.TemplateResponse(
        "customers_table.html",
        {"request": request, "customers": customers}
    )

@router.post("/", response_class=HTMLResponse)
async def create_customer(
    request: Request,
    name: Annotated[str, Form()],
    location: Annotated[Optional[str], Form()] = None,
    contact_person: Annotated[Optional[str], Form()] = None,
    db: Session = Depends(get_db)
):
    new_customer = Customer(
        name=name,
        location=location,
        contact_person=contact_person
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    customers = db.query(Customer).order_by(Customer.name).all()
    return templates.TemplateResponse(
        "customers_table.html",
        {"request": request, "customers": customers}
    )

@router.post("/{customer_id}/contact", response_class=HTMLResponse)
async def update_customer_contact(
    request: Request,
    customer_id: int,
    contact_name: Annotated[str, Form()],
    contact_phone: Annotated[str, Form()],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_required)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Klant niet gevonden")
    
    # RBAC: Admin/Tech can edit all, Client only their own linked customer
    if user.role != Role.ADMIN and user.role != Role.TECHNICUS:
        if customer.user_id != user.id:
            raise HTTPException(status_code=403, detail="Geen toestemming om deze klant te bewerken")

    customer.contact_name = contact_name
    customer.contact_phone = contact_phone
    db.commit()
    
    # Return to the dashboard or customers table depending on where we came from
    # For now, simple redirect
    return RedirectResponse(url=request.headers.get("Referer", "/dashboard"), status_code=303)
