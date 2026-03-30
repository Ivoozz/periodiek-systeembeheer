from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import os
from app.db.session import get_db
from app.models import Report, ReportItem, User, Checkpoint, Category
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import date

router = APIRouter(prefix="/api/v1/external", tags=["External API"])

class ExternalReportIn(BaseModel):
    customer_id: int
    medewerker: str = "PowerShell Script"
    data: Dict[str, Any]

@router.post("/report")
async def create_external_report(
    report_in: ExternalReportIn,
    x_service_token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    # Authenticatie via de .env token
    expected_token = os.getenv("SERVICE_API_TOKEN")
    if not expected_token or x_service_token != expected_token:
        raise HTTPException(status_code=401, detail="Ongeldige of ontbrekende Service API Token")

    # Check of de klant bestaat
    customer = db.query(User).filter(User.id == report_in.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Klant niet gevonden")

    # Nieuw rapport aanmaken
    new_report = Report(
        customer_id=customer.id,
        medewerker=report_in.medewerker,
        datum_uitvoering=date.today(),
        locatie=customer.locatie
    )
    db.add(new_report)
    db.flush()

    # Match data met checkpoints
    for key, value in report_in.data.items():
        # Zoek of er een controlepunt is met deze naam (ongeacht categorie)
        checkpoint = db.query(Checkpoint).filter(Checkpoint.name == key).first()
        categorie_naam = "Algemeen"
        if checkpoint:
            # Haal de categorie op via het checkpoint
            category = db.query(Category).filter(Category.id == checkpoint.category_id).first()
            if category:
                categorie_naam = category.name
        
        # Voeg item toe aan rapport
        # We gaan ervan uit dat als het script data stuurt, het resultaat 'OK' is tenzij anders vermeld
        result = "OK"
        toelichting = str(value)
        if str(value).upper() in ["NOK", "FOUT", "ERROR"]:
            result = "NOK"
        elif str(value).upper() in ["NVT", "NA"]:
            result = "NVT"

        item = ReportItem(
            report_id=new_report.id,
            categorie=categorie_naam,
            controlepunt=key,
            resultaat=result,
            toelichting=toelichting
        )
        db.add(item)

    db.commit()
    db.refresh(new_report)
    return {"message": "Rapport succesvol aangemaakt via API", "report_id": new_report.id}
