from fastapi import APIRouter, Depends, HTTPException, status, Response, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from app.db.session import get_db
from app.models import User
from app.core.auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from pydantic import BaseModel

router = APIRouter(tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(
    response: Response, 
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    login_data: Optional[LoginRequest] = None,
    db: Session = Depends(get_db)
):
    # Handle both Form and JSON input
    user_name = username or (login_data.username if login_data else None)
    user_password = password or (login_data.password if login_data else None)

    if not user_name or not user_password:
        raise HTTPException(status_code=400, detail="Gebruikersnaam en wachtwoord zijn verplicht")

    user = db.query(User).filter(User.username == user_name).first()
    if not user or not verify_password(user_password, user.password_hash):
        # If it's a form request, redirect back with error
        if username:
            return RedirectResponse(url="/login?error=1", status_code=status.HTTP_303_SEE_OTHER)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Onjuiste gebruikersnaam of wachtwoord",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Set cookie for frontend - less restrictive for non-SSL development/LXC environments
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True, 
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Cruciaal voor HTTP verbindingen
    )
    
    # If it's a form request, redirect to dashboard
    if username:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Succesvol uitgelogd"}
