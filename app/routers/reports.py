from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Template, Category, Checkpoint, CustomerCheck, Report, ReportItem, ReportKlantpunt
from app.schemas import ReportCreate, ReportResponse, ReportHistoryItem, TemplateCategory, TemplateCheckpoint
from app.core.auth import get_current_user, require_behandelaar
from app.services.export_service import ExportService

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/template/{customer_id}", response_model=List[TemplateCategory])
def get_report_template(customer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # RBAC: Only Behandelaar or the Klant themselves
    if current_user.role != "Behandelaar" and current_user.id != customer_id:
        raise HTTPException(status_code=403, detail="Toegang geweigerd")

    # Fetch standard template
    # For now, we assume there's only one template or use the first one
    template = db.query(Template).first()
    if not template:
        raise HTTPException(status_code=404, detail="Geen template gevonden")

    categories = db.query(Category).filter(Category.template_id == template.id).all()
    
    result = []
    for cat in categories:
        checkpoints = [TemplateCheckpoint(name=cp.name) for cp in cat.checkpoints]
        result.append(TemplateCategory(name=cat.name, checkpoints=checkpoints))
    
    # Add customer-specific checks
    customer_checks = db.query(CustomerCheck).filter(CustomerCheck.customer_id == customer_id).all()
    if customer_checks:
        cp_list = [TemplateCheckpoint(name=cc.name) for cc in customer_checks]
        result.append(TemplateCategory(name="Klantspecifieke controles", checkpoints=cp_list))
        
    return result

@router.post("", response_model=ReportResponse)
def create_report(report_in: ReportCreate, db: Session = Depends(get_db), current_user: User = Depends(require_behandelaar)):
    # Only Behandelaar can create reports
    new_report = Report(
        customer_id=report_in.customer_id,
        medewerker=report_in.medewerker,
        datum_uitvoering=report_in.datum_uitvoering,
        locatie=report_in.locatie
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    for item in report_in.items:
        db_item = ReportItem(
            report_id=new_report.id,
            categorie=item.categorie,
            controlepunt=item.controlepunt,
            resultaat=item.resultaat,
            toelichting=item.toelichting
        )
        db.add(db_item)
        
    for kp in report_in.klantpunten:
        db_kp = ReportKlantpunt(
            report_id=new_report.id,
            beschrijving=kp.beschrijving,
            uitgevoerde_actie=kp.uitgevoerde_actie
        )
        db.add(db_kp)
        
    db.commit()
    db.refresh(new_report)
    return new_report

@router.get("/history/{customer_id}", response_model=List[ReportHistoryItem])
def get_report_history(customer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # RBAC: Only Behandelaar or the Klant themselves
    if current_user.role != "Behandelaar" and current_user.id != customer_id:
        raise HTTPException(status_code=403, detail="Toegang geweigerd")
        
    reports = db.query(Report).filter(Report.customer_id == customer_id).order_by(Report.datum_uitvoering.desc()).all()
    return reports

@router.get("/{report_id}", response_model=ReportResponse)
def get_report_details(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport niet gevonden")
        
    # RBAC: Only Behandelaar or the Klant whose report it is
    if current_user.role != "Behandelaar" and current_user.id != report.customer_id:
        raise HTTPException(status_code=403, detail="Toegang geweigerd")
        
    return report

@router.get("/{id}/export/word")
def export_report_word(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport niet gevonden")
    
    # RBAC: Only Behandelaar or the Klant whose report it is
    if current_user.role != "Behandelaar" and current_user.id != report.customer_id:
        raise HTTPException(status_code=403, detail="Toegang geweigerd")
    
    customer = db.query(User).filter(User.id == report.customer_id).first()
    buffer = ExportService.generate_word_report(report, customer)
    
    filename = f"Rapport_{report.datum_uitvoering.strftime('%Y%m%d')}_{customer.username}.docx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/{id}/export/excel")
def export_report_excel(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport niet gevonden")
    
    # RBAC: Only Behandelaar or the Klant whose report it is
    if current_user.role != "Behandelaar" and current_user.id != report.customer_id:
        raise HTTPException(status_code=403, detail="Toegang geweigerd")
    
    customer = db.query(User).filter(User.id == report.customer_id).first()
    buffer = ExportService.generate_excel_report(report, customer)
    
    filename = f"Rapport_{report.datum_uitvoering.strftime('%Y%m%d')}_{customer.username}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
