import pytest
from sqlalchemy.orm import Session
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Customer, Role
try:
    from app.db.models import Assignment
except ImportError:
    Assignment = None
import datetime

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_customer_extended_fields(db_session: Session):
    # This should fail if contact_name or contact_phone are missing
    c1 = Customer(
        name="Test Customer",
        location="Test Loc",
        contact_person="Old Contact",
        contact_name="New Contact Name",
        contact_phone="0612345678"
    )
    db_session.add(c1)
    db_session.commit()
    db_session.refresh(c1)
    
    assert c1.contact_name == "New Contact Name"
    assert c1.contact_phone == "0612345678"

def test_assignment_model_exists():
    assert Assignment is not None, "Assignment model should be defined in app/db/models.py"

def test_create_assignment(db_session: Session):
    if Assignment is None:
        pytest.fail("Assignment model not found")
        
    # Create a technician and a customer first
    tech = User(username="tech1", password_hash="hash", role=Role.TECHNICUS)
    cust = Customer(name="Cust1")
    db_session.add_all([tech, cust])
    db_session.commit()
    
    # Create assignment
    now = datetime.datetime.utcnow()
    assignment = Assignment(
        customer_id=cust.id,
        technician_id=tech.id,
        scheduled_date=now,
        status="Planned",
        is_recurring=True,
        interval_days=90
    )
    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(assignment)
    
    assert assignment.id is not None
    assert assignment.customer_id == cust.id
    assert assignment.technician_id == tech.id
    assert assignment.status == "Planned"
    assert assignment.is_recurring is True
    assert assignment.interval_days == 90
    
    # Check relationships
    assert assignment.customer.name == "Cust1"
    assert assignment.technician.username == "tech1"
