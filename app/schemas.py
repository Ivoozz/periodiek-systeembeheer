from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    role: str # 'Behandelaar' or 'Klant'
    locatie: Optional[str] = None
    next_maintenance_date: Optional[date] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    locatie: Optional[str] = None
    next_maintenance_date: Optional[date] = None

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PasswordChange(BaseModel):
    old_password: Optional[str] = None # Only needed for self-service
    new_password: str

class AdminPasswordChange(BaseModel):
    user_id: int
    new_password: str

class SystemSettingsBase(BaseModel):
    header_text: Optional[str] = None
    footer_text: Optional[str] = None

class SystemSettingsUpdate(SystemSettingsBase):
    pass

class SystemSettingsResponse(SystemSettingsBase):
    id: int
    logo_url: Optional[str] = None
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ... Other existing schemas (Report, Checkpoint, etc.) ...
# I will keep them but focus on the requested changes now.
