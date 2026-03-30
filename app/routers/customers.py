from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app import models, schemas
from app.core import auth

router = APIRouter(
    prefix="/api/customers",
    tags=["customers"],
    dependencies=[Depends(auth.require_behandelaar)]
)

@router.get("/", response_model=List[schemas.CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == "Klant").all()

@router.post("/", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer_data: schemas.CustomerCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    existing_user = db.query(models.User).filter(models.User.username == customer_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gebruikersnaam bestaat al"
        )
    
    new_customer = models.User(
        username=customer_data.username,
        password_hash=auth.get_password_hash(customer_data.password),
        role="Klant"
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(id: int, db: Session = Depends(get_db)):
    customer = db.query(models.User).filter(models.User.id == id, models.User.role == "Klant").first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Klant niet gevonden"
        )
    
    db.delete(customer)
    db.commit()
    return None

@router.get("/{id}/checks", response_model=List[schemas.CustomerCheckResponse])
def get_customer_checks(id: int, db: Session = Depends(get_db)):
    # Verify customer exists
    customer = db.query(models.User).filter(models.User.id == id, models.User.role == "Klant").first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Klant niet gevonden"
        )
    
    return db.query(models.CustomerCheck).filter(models.CustomerCheck.customer_id == id).all()

@router.post("/{id}/checks", response_model=schemas.CustomerCheckResponse, status_code=status.HTTP_201_CREATED)
def create_customer_check(id: int, check_data: schemas.CustomerCheckCreate, db: Session = Depends(get_db)):
    # Verify customer exists
    customer = db.query(models.User).filter(models.User.id == id, models.User.role == "Klant").first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Klant niet gevonden"
        )
    
    new_check = models.CustomerCheck(
        customer_id=id,
        name=check_data.name
    )
    db.add(new_check)
    db.commit()
    db.refresh(new_check)
    return new_check
