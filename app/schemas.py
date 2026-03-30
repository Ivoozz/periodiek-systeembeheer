from pydantic import BaseModel
from typing import Optional, List

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class CustomerCreate(BaseModel):
    username: str
    password: str

class CustomerCheckCreate(BaseModel):
    name: str

class CustomerCheckResponse(BaseModel):
    id: int
    customer_id: int
    name: str

    class Config:
        from_attributes = True

class CustomerResponse(BaseModel):
    id: int
    username: str
    role: str
    customer_checks: List[CustomerCheckResponse] = []

    class Config:
        from_attributes = True

# Report schemas
class ReportItemBase(BaseModel):
    categorie: str
    controlepunt: str
    resultaat: str
    toelichting: Optional[str] = None

class ReportItemCreate(ReportItemBase):
    pass

class ReportItemResponse(ReportItemBase):
    id: int
    report_id: int

    class Config:
        from_attributes = True

class ReportKlantpuntBase(BaseModel):
    beschrijving: str
    uitgevoerde_actie: str

class ReportKlantpuntCreate(ReportKlantpuntBase):
    pass

class ReportKlantpuntResponse(ReportKlantpuntBase):
    id: int
    report_id: int

    class Config:
        from_attributes = True

from datetime import date, datetime

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

    class Config:
        from_attributes = True

class ReportHistoryItem(BaseModel):
    id: int
    customer_id: int
    medewerker: str
    datum_uitvoering: date
    locatie: str
    created_at: datetime

    class Config:
        from_attributes = True

# Template schemas
class TemplateCheckpoint(BaseModel):
    name: str

class TemplateCategory(BaseModel):
    name: str
    checkpoints: List[TemplateCheckpoint]
