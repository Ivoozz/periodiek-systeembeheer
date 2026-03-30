from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Report, ReportItem, Checkpoint, Category, User, CustomerCheck
from app.core.config import settings
from pydantic import BaseModel
from typing import Dict
from datetime import date

router = APIRouter(prefix="/api/v1/external", tags=["External"])

class ExternalReportRequest(BaseModel):
    customer_id: int
    medewerker: str
    data: Dict[str, str]

def verify_service_token(x_service_token: str = Header(...)):
    if x_service_token != settings.SERVICE_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service token",
        )
    return x_service_token

@router.post("/report")
def create_external_report(
    request: ExternalReportRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_service_token)
):
    # Check if customer exists
    customer = db.query(User).filter(User.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create new report
    new_report = Report(
        customer_id=request.customer_id,
        medewerker=request.medewerker,
        datum_uitvoering=date.today(),
        locatie="Remote PowerShell"
    )
    db.add(new_report)
    db.flush() # Get the id

    for checkpoint_name, result in request.data.items():
        # Try to find the checkpoint to get the category
        checkpoint = db.query(Checkpoint).filter(Checkpoint.name == checkpoint_name).first()
        
        category_name = "External"
        if checkpoint:
            category = db.query(Category).filter(Category.id == checkpoint.category_id).first()
            if category:
                category_name = category.name
        else:
            # Check customer specific checks
            customer_check = db.query(CustomerCheck).filter(
                CustomerCheck.customer_id == request.customer_id,
                CustomerCheck.name == checkpoint_name
            ).first()
            if customer_check:
                category_name = "Klantspecifieke controles"
        
        report_item = ReportItem(
            report_id=new_report.id,
            categorie=category_name,
            controlepunt=checkpoint_name,
            resultaat=result,
            toelichting="Automatically reported by external service"
        )
        db.add(report_item)
    
    db.commit()
    db.refresh(new_report)
    return {"status": "success", "report_id": new_report.id}
