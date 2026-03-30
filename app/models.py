from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String) # 'Behandelaar' of 'Klant'
    locatie = Column(String, nullable=True)
    next_maintenance_date = Column(Date, nullable=True)
    customer_checks = relationship("CustomerCheck", back_populates="customer")
    reports = relationship("Report", back_populates="customer")

class CustomerCheck(Base):
    __tablename__ = "customer_checks"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String) # Het controlepunt
    customer = relationship("User", back_populates="customer_checks")

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    categories = relationship("Category", back_populates="template")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    template_id = Column(Integer, ForeignKey("templates.id"))
    template = relationship("Template", back_populates="categories")
    checkpoints = relationship("Checkpoint", back_populates="category")

class Checkpoint(Base):
    __tablename__ = "checkpoints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="checkpoints")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    medewerker = Column(String)
    datum_uitvoering = Column(Date)
    locatie = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("User", back_populates="reports")
    items = relationship("ReportItem", back_populates="report", cascade="all, delete-orphan")
    klantpunten = relationship("ReportKlantpunt", back_populates="report", cascade="all, delete-orphan")
    
class ReportItem(Base):
    __tablename__ = "report_items"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    categorie = Column(String)
    controlepunt = Column(String)
    resultaat = Column(String) # 'OK', 'NOK', 'NVT'
    toelichting = Column(String, nullable=True)
    report = relationship("Report", back_populates="items")

class ReportKlantpunt(Base):
    __tablename__ = "report_klantpunten"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    beschrijving = Column(String)
    uitgevoerde_actie = Column(String)
    report = relationship("Report", back_populates="klantpunten")

class SystemSettings(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True, index=True)
    logo_url = Column(String, nullable=True)
    header_text = Column(String, nullable=True)
    footer_text = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
