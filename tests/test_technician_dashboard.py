import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role, Customer, Assignment, AssignmentStatus
from app.core.auth import get_password_hash
import datetime

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_technician_dashboard_access_denied_for_anonymous(db_session):
    response = client.get("/behandelaar/dashboard")
    assert response.status_code == 401 # get_current_user_required raises 401

def test_technician_dashboard_content(db_session):
    # Create a technician
    tech_user = User(
        username="tech1",
        password_hash=get_password_hash("password"),
        role=Role.TECHNICUS,
        is_active=True
    )
    db_session.add(tech_user)
    db_session.commit()
    db_session.refresh(tech_user)

    # Create a customer
    customer = Customer(
        name="Test Klant",
        location="Amsterdam",
        contact_name="Jan Jansen",
        contact_phone="0612345678"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    # Create an assignment
    assignment = Assignment(
        customer_id=customer.id,
        technician_id=tech_user.id,
        scheduled_date=datetime.datetime.now(),
        status=AssignmentStatus.PLANNED
    )
    db_session.add(assignment)
    db_session.commit()

    # Log in as technician
    response = client.post("/login", data={"username": "tech1", "password": "password"})
    assert response.status_code == 200 # Redirect followed or successful login

    # Access dashboard
    response = client.get("/behandelaar/dashboard")
    assert response.status_code == 200
    assert "Test Klant" in response.text
    assert "Jan Jansen" in response.text
    assert "0612345678" in response.text
    assert "Amsterdam" in response.text
    assert "Start Inspectie" in response.text
