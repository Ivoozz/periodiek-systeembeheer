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

# --- Report Schemas ---

class ReportItemBase(BaseModel):
    categorie: str
    controlepunt: str
    resultaat: str # 'OK', 'NOK', 'NVT'
    toelichting: Optional[str] = None

class ReportItemCreate(ReportItemBase):
    pass

class ReportItemResponse(ReportItemBase):
    id: int
    report_id: int
    model_config = ConfigDict(from_attributes=True)

class ReportKlantpuntBase(BaseModel):
    beschrijving: str
    uitgevoerde_actie: str

class ReportKlantpuntCreate(ReportKlantpuntBase):
    pass

class ReportKlantpuntResponse(ReportKlantpuntBase):
    id: int
    report_id: int
    model_config = ConfigDict(from_attributes=True)

class ReportBase(BaseModel):
    customer_id: int
    medewerker: str
    datum_uitvoering: date
    locatie: str

class ReportCreate(ReportBase):
    items: List[ReportItemCreate]
    klantpunten: List[ReportKlantpuntCreate]

class ReportResponse(ReportBase):
    id: int
    created_at: datetime
    items: List[ReportItemResponse]
    klantpunten: List[ReportKlantpuntResponse]
    model_config = ConfigDict(from_attributes=True)

class ReportHistoryItem(ReportBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Template Schemas ---

class TemplateCheckpoint(BaseModel):
    name: str

class TemplateCategory(BaseModel):
    name: str
    checkpoints: List[TemplateCheckpoint]

# --- Customer Schemas ---

class CustomerBase(BaseModel):
    username: str

class CustomerCreate(CustomerBase):
    password: str

class CustomerResponse(CustomerBase):
    id: int
    role: str
    locatie: Optional[str] = None
    next_maintenance_date: Optional[date] = None
    model_config = ConfigDict(from_attributes=True)

class CustomerCheckBase(BaseModel):
    name: str

class CustomerCheckCreate(CustomerCheckBase):
    pass

class CustomerCheckResponse(CustomerCheckBase):
    id: int
    customer_id: int
    model_config = ConfigDict(from_attributes=True)
