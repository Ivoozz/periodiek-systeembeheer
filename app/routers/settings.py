from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import shutil
import os
from app.db.session import get_db
from app.models import SystemSettings, User
from app.core.auth import get_current_user
from app.schemas import SystemSettingsResponse

router = APIRouter(prefix="/settings", tags=["Settings"])

UPLOAD_DIR = "/var/www/systeembeheer/app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=SystemSettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(SystemSettings).first()
    if not settings:
        # Create default
        settings = SystemSettings(header_text="Periodiek Systeembeheer", footer_text="© 2026 Systeembeheer")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.post("/", response_model=SystemSettingsResponse)
async def update_settings(
    header_text: Optional[str] = Form(None),
    footer_text: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Behandelaar":
        raise HTTPException(status_code=403, detail="Alleen beheerders kunnen instellingen wijzigen")
    
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
    
    if header_text is not None:
        settings.header_text = header_text
    if footer_text is not None:
        settings.footer_text = footer_text
        
    if logo:
        file_ext = logo.filename.split(".")[-1]
        file_path = f"{UPLOAD_DIR}/logo.{file_ext}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
        settings.logo_url = f"/static/uploads/logo.{file_ext}"
    
    db.commit()
    db.refresh(settings)
    return settings
