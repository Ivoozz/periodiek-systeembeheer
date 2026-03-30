from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, PasswordChange, AdminPasswordChange
from app.core.auth import get_current_user, get_password_hash, verify_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_my_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify old password
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Huidig wachtwoord is onjuist")
    
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Wachtwoord succesvol gewijzigd"}

@router.post("/admin-change-password")
def admin_change_password(
    data: AdminPasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Behandelaar":
        raise HTTPException(status_code=403, detail="Alleen beheerders kunnen wachtwoorden van anderen wijzigen")
    
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Gebruiker niet gevonden")
    
    user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": f"Wachtwoord voor {user.username} succesvol gewijzigd"}

@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Behandelaar":
        return [current_user]
    return db.query(User).all()

# ... Add user creation if needed ...
@router.post("/", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Behandelaar":
        raise HTTPException(status_code=403, detail="Niet geautoriseerd")
        
    db_user = db.query(User).filter(User.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Gebruiker bestaat al")
        
    new_user = User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
        locatie=user_in.locatie,
        next_maintenance_date=user_in.next_maintenance_date
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
