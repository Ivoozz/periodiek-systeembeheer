from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime
import enum
from .database import Base

class Role(str, enum.Enum):
    ADMIN = "Admin"
    TECHNICUS = "Technicus"
    CLIENT = "Client"

class ResultStatus(str, enum.Enum):
    OK = "OK"
    NOK = "NOK"
    NVT = "NVT"

class ReportStatus(str, enum.Enum):
    CONCEPT = "Concept"
    FINAL = "Final"

class AssignmentStatus(str, enum.Enum):
    PLANNED = "Planned"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class WhitelabelSettings(Base):
    __tablename__ = "whitelabel_settings"
    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String, default="Periodiek Systeembeheer")
    logo_url = Column(String, nullable=True)
    primary_color = Column(String, default="#3498db")
    secondary_color = Column(String, default="#2c3e50")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.TECHNICUS)
    is_active = Column(Boolean, default=True)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    contact_person = Column(String)
    contact_name = Column(String)
    contact_phone = Column(String)
    interval_days = Column(Integer, default=30)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    technician_id = Column(Integer, ForeignKey("users.id"))
    scheduled_date = Column(DateTime)
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.PLANNED)
    is_recurring = Column(Boolean, default=False)
    interval_days = Column(Integer, default=30)
    
    customer = relationship("Customer")
    technician = relationship("User")

class ChecklistTemplate(Base):
    __tablename__ = "checklist_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    categories = relationship("Category", back_populates="template", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("checklist_templates.id"))
    name = Column(String, nullable=False)
    order = Column(Integer, default=0)
    template = relationship("ChecklistTemplate", back_populates="categories")
    checkpoints = relationship("Checkpoint", back_populates="category", cascade="all, delete-orphan")

class Checkpoint(Base):
    __tablename__ = "checkpoints"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    category = relationship("Category", back_populates="checkpoints")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    technician_id = Column(Integer, ForeignKey("users.id"))
    date_performed = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Enum(ReportStatus), default=ReportStatus.CONCEPT)
    
    customer = relationship("Customer")
    technician = relationship("User")
    items = relationship("ReportItem", back_populates="report", cascade="all, delete-orphan")

class ReportItem(Base):
    __tablename__ = "report_items"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    checkpoint_id = Column(Integer, ForeignKey("checkpoints.id"))
    result = Column(Enum(ResultStatus), default=ResultStatus.NVT)
    comment = Column(Text)
    
    report = relationship("Report", back_populates="items")
    checkpoint = relationship("Checkpoint")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False) # e.g., "CREATE", "UPDATE", "DELETE"
    target_type = Column(String, nullable=False) # e.g., "Customer", "User"
    target_id = Column(Integer, nullable=False)
    details = Column(Text, nullable=True) # JSON or descriptive text
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
