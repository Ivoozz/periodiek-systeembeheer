from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import datetime

from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/api/v1", tags=["External API"])

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# In a production app, these would be in the DB
# For this rebuild, we use an env-configurable key
import os
VALID_API_KEY = os.getenv("EXTERNAL_API_KEY", "po-secret-api-key-2026")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == VALID_API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Ongeldige API Key"
    )

class ReportItemSchema(BaseModel):
    checkpoint_id: int
    result: str # OK, NOK, NVT
    comment: Optional[str] = ""

class ExternalReportSchema(BaseModel):
    customer_id: int
    items: List[ReportItemSchema]

@router.post("/reports")
async def receive_external_report(
    data: ExternalReportSchema,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    # Verify customer
    customer = db.query(models.Customer).filter(models.Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Klant niet gevonden")
    
    # Create report (system-generated)
    report = models.Report(
        customer_id=data.customer_id,
        technician_id=1, # Default to first admin for automated reports
        date_performed=datetime.datetime.now(datetime.timezone.utc),
        status=models.ReportStatus.FINAL
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    for item in data.items:
        report_item = models.ReportItem(
            report_id=report.id,
            checkpoint_id=item.checkpoint_id,
            result=models.ResultStatus(item.result),
            comment=item.comment
        )
        db.add(report_item)
    
    db.commit()
    
    # Recurring Task Logic
    if customer.interval_days:
        next_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=customer.interval_days)
        new_assignment = models.Assignment(
            customer_id=customer.id,
            technician_id=1, # Default admin
            scheduled_date=next_date,
            status=models.AssignmentStatus.PLANNED,
            is_recurring=True,
            interval_days=customer.interval_days
        )
        db.add(new_assignment)
        db.commit()

    return {"status": "success", "report_id": report.id}
