import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role, Customer, Assignment, AssignmentStatus
from app.core.auth import get_password_hash, create_session_cookie, SESSION_COOKIE_NAME
from datetime import datetime

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

@pytest.fixture
def admin_client(db_session: Session):
    # Create test admin user
    test_user = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        role=Role.ADMIN,
        is_active=True
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    
    # Create session cookie
    token = create_session_cookie(test_user.id)
    client.cookies.set(SESSION_COOKIE_NAME, token)
    return client

@pytest.fixture
def tech_client(db_session: Session):
    # Create test technician user
    test_user = User(
        username="technician",
        password_hash=get_password_hash("tech123"),
        role=Role.TECHNICUS,
        is_active=True
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    
    # Create session cookie
    token = create_session_cookie(test_user.id)
    client.cookies.set(SESSION_COOKIE_NAME, token)
    return client

def test_planning_page_admin(admin_client, db_session: Session):
    # Setup some data
    customer = Customer(name="Customer A")
    technician = User(username="tech1", password_hash="...", role=Role.TECHNICUS)
    db_session.add_all([customer, technician])
    db_session.commit()
    
    assignment = Assignment(customer_id=customer.id, technician_id=technician.id, scheduled_date=datetime(2025, 5, 20, 10, 0))
    db_session.add(assignment)
    db_session.commit()
    
    response = admin_client.get("/admin/planning")
    assert response.status_code == 200
    assert "Planning" in response.text
    assert "Customer A" in response.text
    assert "tech1" in response.text

def test_planning_page_unauthorized(tech_client, db_session: Session):
    response = tech_client.get("/admin/planning")
    assert response.status_code == 403

def test_assign_assignment(admin_client, db_session: Session):
    customer = Customer(name="Customer B")
    technician = User(username="tech2", password_hash="...", role=Role.TECHNICUS)
    db_session.add_all([customer, technician])
    db_session.commit()
    
    response = admin_client.post("/admin/planning/assign", data={
        "customer_id": customer.id,
        "technician_id": technician.id,
        "scheduled_date": "2025-06-15T14:30"
    })
    
    # After POST it should redirect or return a fragment
    assert response.status_code in [200, 303]
    
    assignment = db_session.query(Assignment).filter(Assignment.customer_id == customer.id).first()
    assert assignment is not None
    assert assignment.technician_id == technician.id
    assert assignment.scheduled_date == datetime(2025, 6, 15, 14, 30)
