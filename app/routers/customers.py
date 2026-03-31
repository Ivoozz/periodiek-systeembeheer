from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from app.db.database import get_db
from app.db.models import Customer, User
from app.core.auth import get_current_user_required
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/customers", tags=["customers"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def list_customers(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_required),
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
    user: User = Depends(get_current_user_required),
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
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_required)
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

@router.delete("/{customer_id}", response_class=HTMLResponse)
async def delete_customer(
    request: Request,
    customer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_required)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    
    customers = db.query(Customer).order_by(Customer.name).all()
    return templates.TemplateResponse(
        "customers_table.html",
        {"request": request, "customers": customers}
    )
