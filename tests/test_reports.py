import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role, Customer, ChecklistTemplate, Category, Checkpoint, Report, ReportItem, ResultStatus
from app.core.auth import get_password_hash, create_session_cookie, SESSION_COOKIE_NAME

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Create a default template and some checkpoints
        template = ChecklistTemplate(name="Standard Template")
        db.add(template)
        db.commit()
        db.refresh(template)
        
        cat1 = Category(name="Server", template_id=template.id)
        db.add(cat1)
        db.commit()
        db.refresh(cat1)
        
        cp1 = Checkpoint(name="Check Disk Space", category_id=cat1.id)
        cp2 = Checkpoint(name="Check Backups", category_id=cat1.id)
        db.add_all([cp1, cp2])
        db.commit()
        
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_client(db_session: Session):
    # Create test user
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

def test_get_report_form(auth_client, db_session: Session):
    customer = Customer(name="Test Customer")
    db_session.add(customer)
    db_session.commit()
    
    response = auth_client.get(f"/reports/new/{customer.id}")
    assert response.status_code == 200
    assert "Test Customer" in response.text
    assert "Check Disk Space" in response.text

def test_create_report(auth_client, db_session: Session):
    customer = Customer(name="Test Customer")
    db_session.add(customer)
    db_session.commit()
    
    checkpoint = db_session.query(Checkpoint).first()
    
    data = {
        "customer_id": customer.id,
        f"checkpoint_{checkpoint.id}_result": "OK",
        f"checkpoint_{checkpoint.id}_comment": "All good"
    }
    
    response = auth_client.post("/reports", data=data)
    assert response.status_code == 200 # Or 303 Redirect
    
    report = db_session.query(Report).filter(Report.customer_id == customer.id).first()
    assert report is not None
    assert len(report.items) > 0
    assert report.items[0].result == ResultStatus.OK
    assert report.items[0].comment == "All good"

def test_view_report(auth_client, db_session: Session):
    customer = Customer(name="Test Customer")
    db_session.add(customer)
    db_session.commit()
    
    report = Report(customer_id=customer.id, technician_id=1) # Assuming user id 1 is the admin
    db_session.add(report)
    db_session.commit()
    
    response = auth_client.get(f"/reports/{report.id}")
    assert response.status_code == 200
    assert "Test Customer" in response.text

def test_export_report(auth_client, db_session: Session):
    customer = Customer(name="Test Customer")
    db_session.add(customer)
    db_session.commit()
    
    report = Report(customer_id=customer.id, technician_id=1)
    db_session.add(report)
    db_session.commit()
    
    response = auth_client.get(f"/reports/{report.id}/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
