import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role, Customer, ChecklistTemplate, Category, Checkpoint, Report, ReportItem, ResultStatus, Assignment, AssignmentStatus
from app.core.auth import get_password_hash, create_session_cookie, SESSION_COOKIE_NAME
import datetime

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
        db.add_all([cp1])
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

def test_recurring_assignment_creation(auth_client, db_session: Session):
    # 1. Setup customer with interval_days
    customer = Customer(name="Test Customer", interval_days=14)
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    checkpoint = db_session.query(Checkpoint).first()
    
    # 2. POST report to /reports and check if a new assignment is created
    # Note: we need to make sure the endpoint marks it as FINAL or we trigger it.
    # The task says: "If a report is finalized and the customer has an interval_days set"
    # Let's see if we can add a 'finalize' flag to the form or if it's always final.
    
    data = {
        "customer_id": customer.id,
        f"checkpoint_{checkpoint.id}_result": "OK",
        f"checkpoint_{checkpoint.id}_comment": "All good",
        "finalize": "true" # I'll add this to the router
    }
    
    response = auth_client.post("/reports", data=data)
    assert response.status_code == 303 # Redirect to report view
    
    # 3. Verify new assignment is created
    new_assignment = db_session.query(Assignment).filter(
        Assignment.customer_id == customer.id,
        Assignment.status == AssignmentStatus.PLANNED
    ).first()
    
    assert new_assignment is not None
    # Use .date() for comparison to avoid time differences
    today = datetime.datetime.now(datetime.timezone.utc).date()
    expected_date = today + datetime.timedelta(days=14)
    assert new_assignment.scheduled_date.date() == expected_date
