from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import WhitelabelSettings, User, AuditLog
from app.core.auth import require_admin
from app.core.templates import templates

router = APIRouter(prefix="/admin", tags=["settings"])

@router.get("/settings")
async def get_settings(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    settings = db.query(WhitelabelSettings).first()
    if not settings:
        settings = WhitelabelSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "settings": settings, "user": admin}
    )

@router.post("/settings")
async def update_settings(
    request: Request,
    brand_name: str = Form(...),
    logo_url: str = Form(None),
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    settings = db.query(WhitelabelSettings).first()
    if not settings:
        settings = WhitelabelSettings()
        db.add(settings)
    
    old_name = settings.brand_name
    settings.brand_name = brand_name
    settings.logo_url = logo_url
    settings.primary_color = primary_color
    settings.secondary_color = secondary_color
    
    # Audit Log
    db.add(AuditLog(
        user_id=admin.id,
        action="UPDATE",
        target_type="WhitelabelSettings",
        target_id=settings.id or 0,
        details=f"Branding gewijzigd: {old_name} -> {brand_name}"
    ))
    
    db.commit()
    
    return RedirectResponse(url="/admin/settings", status_code=status.HTTP_303_SEE_OTHER)
