from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.core.auth import get_current_user_required, get_password_hash
from app.core.templates import templates

router = APIRouter(tags=["profile"])

@router.get("/profile")
async def get_profile(
    request: Request,
    user: User = Depends(get_current_user_required)
):
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user}
    )

@router.post("/profile")
async def update_profile(
    request: Request,
    display_name: str = Form(...),
    password: str = Form(None),
    confirm_password: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_required)
):
    user.display_name = display_name
    
    if password:
        if password != confirm_password:
            return templates.TemplateResponse(
                "profile.html",
                {"request": request, "user": user, "error": "Wachtwoorden komen niet overeen"}
            )
        user.password_hash = get_password_hash(password)
    
    db.commit()
    
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "success": "Profiel succesvol bijgewerkt"}
    )
