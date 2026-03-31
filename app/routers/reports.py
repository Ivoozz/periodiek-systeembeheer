from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated, Optional
import io
from datetime import datetime, timezone, timedelta

from app.db.database import get_db
from app.db import models
from app.core.auth import get_current_user_required
from app.services.export_service import generate_word_report

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/new/{customer_id}", response_class=HTMLResponse)
async def new_report_form(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user_required)
):
    # Check if technician is assigned to this customer (Admins can do everything)
    if user.role != models.Role.ADMIN:
        assignment = db.query(models.Assignment).filter(
            models.Assignment.customer_id == customer_id,
            models.Assignment.technician_id == user.id,
            models.Assignment.status == models.AssignmentStatus.PLANNED
        ).first()
        if not assignment:
            raise HTTPException(status_code=403, detail="Toegang geweigerd: Je bent niet ingeroosterd voor deze klant.")

    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Use the first available template
    template = db.query(models.ChecklistTemplate).first()
    if not template:
        # Fallback
        template = models.ChecklistTemplate(name="Standaard Controle", description="Automatisch gegenereerd")
        db.add(template)
        db.commit()
        db.refresh(template)
        
    return templates.TemplateResponse("report_form.html", {
        "request": request,
        "customer": customer,
        "template": template,
        "user": user
    })

@router.post("", response_class=HTMLResponse)
async def create_report(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user_required)
):
    form_data = await request.form()
    customer_id = int(form_data.get("customer_id"))

    # Check if technician is assigned to this customer (Admins can do everything)
    if user.role != models.Role.ADMIN:
        assignment = db.query(models.Assignment).filter(
            models.Assignment.customer_id == customer_id,
            models.Assignment.technician_id == user.id,
            models.Assignment.status == models.AssignmentStatus.PLANNED
        ).first()
        if not assignment:
            raise HTTPException(status_code=403, detail="Toegang geweigerd: Je bent niet ingeroosterd voor deze klant.")
        
        # Also mark the assignment as COMPLETED
        if form_data.get("finalize") == "true":
            assignment.status = models.AssignmentStatus.COMPLETED
            db.add(assignment)

    finalize = form_data.get("finalize") == "true"
    
    report_status = models.ReportStatus.FINAL if finalize else models.ReportStatus.CONCEPT
    
    report = models.Report(
        customer_id=customer_id,
        technician_id=user.id,
        date_performed=datetime.now(timezone.utc),
        status=report_status
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Process checkpoints
    for key in form_data.keys():
        if key.startswith("checkpoint_") and key.endswith("_result"):
            checkpoint_id = int(key.split("_")[1])
            result_val = form_data.get(key)
            comment = form_data.get(f"checkpoint_{checkpoint_id}_comment", "")
            
            if result_val:
                item = models.ReportItem(
                    report_id=report.id,
                    checkpoint_id=checkpoint_id,
                    result=models.ResultStatus(result_val),
                    comment=comment
                )
                db.add(item)
    
    db.commit()
    
    # Recurring Task Logic
    if finalize:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        if customer and customer.interval_days and customer.interval_days > 0:
            next_date = datetime.now(timezone.utc) + timedelta(days=customer.interval_days)
            new_assignment = models.Assignment(
                customer_id=customer.id,
                technician_id=user.id,
                scheduled_date=next_date,
                status=models.AssignmentStatus.PLANNED,
                is_recurring=True,
                interval_days=customer.interval_days
            )
            db.add(new_assignment)
            db.commit()

    return RedirectResponse(url=f"/reports/{report.id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{report_id}", response_class=HTMLResponse)
async def view_report(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user_required)
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport niet gevonden")
    
    # IDOR Check
    if user.role != models.Role.ADMIN and report.technician_id != user.id:
        raise HTTPException(status_code=403, detail="Toegang geweigerd: Je kunt alleen je eigen rapporten inzien.")

    return templates.TemplateResponse("report_view.html", {
        "request": request,
        "report": report,
        "user": user
    })

@router.get("/{report_id}/export")
async def export_report(
    report_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user_required)
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport niet gevonden")
    
    # IDOR Check
    if user.role != models.Role.ADMIN and report.technician_id != user.id:
        raise HTTPException(status_code=403, detail="Toegang geweigerd")

    doc = generate_word_report(report)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    filename = f"Rapport_{report.customer.name}_{report.date_performed.strftime('%Y%m%d')}.docx"
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
