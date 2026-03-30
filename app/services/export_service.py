import os
from docx import Document
from openpyxl import Workbook
from datetime import datetime
from app.models import Report, User
from io import BytesIO

class ExportService:
    @staticmethod
    def generate_word_report(report: Report, customer: User):
        # Absoluut pad voor productie
        template_path = "/var/www/systeembeheer/app/templates/exports/template.docx"
        
        if os.path.exists(template_path):
            doc = Document(template_path)
        else:
            doc = Document()
            doc.add_heading('Periodiek Systeembeheer Rapportage', 0)

        placeholders = {
            "{{ KLANT_NAAM }}": customer.username,
            "{{ LOCATIE }}": report.locatie or "-",
            "{{ DATUM }}": report.datum_uitvoering.strftime("%d-%m-%Y"),
            "{{ MEDEWERKER }}": report.medewerker
        }

        for paragraph in doc.paragraphs:
            for key, value in placeholders.items():
                if key in paragraph.text:
                    paragraph.text = paragraph.text.replace(key, value)

        doc.add_heading('Checklist Resultaten', level=1)
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Categorie'
        hdr_cells[1].text = 'Controlepunt'
        hdr_cells[2].text = 'Resultaat'
        hdr_cells[3].text = 'Toelichting'

        for item in report.items:
            row_cells = table.add_row().cells
            row_cells[0].text = item.categorie
            row_cells[1].text = item.controlepunt
            row_cells[2].text = item.resultaat
            row_cells[3].text = item.toelichting or ""

        if report.klantpunten:
            doc.add_heading('Klantpunten (Acties)', level=1)
            kp_table = doc.add_table(rows=1, cols=2)
            kp_table.style = 'Table Grid'
            hdr_cells = kp_table.rows[0].cells
            hdr_cells[0].text = 'Beschrijving'
            hdr_cells[1].text = 'Uitgevoerde actie'

            for kp in report.klantpunten:
                row_cells = kp_table.add_row().cells
                row_cells[0].text = kp.beschrijving
                row_cells[1].text = kp.uitgevoerde_actie

        target = BytesIO()
        doc.save(target)
        target.seek(0)
        return target

    @staticmethod
    def generate_excel_report(report: Report, customer: User):
        wb = Workbook()
        ws = wb.active
        ws.title = "Onderhoudsrapport"

        ws.append(["Klant", customer.username])
        ws.append(["Datum", report.datum_uitvoering.strftime("%d-%m-%Y")])
        ws.append(["Medewerker", report.medewerker])
        ws.append([])

        ws.append(["Categorie", "Controlepunt", "Resultaat", "Toelichting"])
        for item in report.items:
            ws.append([item.categorie, item.controlepunt, item.resultaat, item.toelichting or ""])

        if report.klantpunten:
            ws.append([])
            ws.append(["KLANTPUNTEN"])
            ws.append(["Beschrijving", "Uitgevoerde actie"])
            for kp in report.klantpunten:
                ws.append([kp.beschrijving, kp.uitgevoerde_actie])

        target = BytesIO()
        wb.save(target)
        target.seek(0)
        return target
