import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db import models
from app.core.auth import get_password_hash, create_session_cookie, SESSION_COOKIE_NAME
import datetime
import os

# Set DATABASE_PATH to something else for testing if needed
# os.environ["DATABASE_PATH"] = ":memory:" # Wait, database.py uses DB_PATH from env

def test_full_lifecycle():
    # Setup
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Create User
    user = models.User(username="tech1", password_hash=get_password_hash("test"), role=models.Role.TECHNICUS)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 2. Create Customer
    customer = models.Customer(name="Test Corp", location="Utrecht", interval_days=30)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    # 3. Create Checklist Template
    template = models.ChecklistTemplate(name="Standard")
    db.add(template)
    db.commit()
    db.refresh(template)
    cat = models.Category(name="General", template_id=template.id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    cp = models.Checkpoint(name="Check UPS", category_id=cat.id)
    db.add(cp)
    db.commit()
    db.refresh(cp)
    
    # 4. Create Assignment
    assignment = models.Assignment(
        customer_id=customer.id,
        technician_id=user.id,
        scheduled_date=datetime.datetime.now() + datetime.timedelta(days=1),
        status=models.AssignmentStatus.PLANNED
    )
    db.add(assignment)
    db.commit()
    
    # Login
    client = TestClient(app)
    token = create_session_cookie(user.id)
    client.cookies.set(SESSION_COOKIE_NAME, token)
    
    # 5. Create Report (finalize = true)
    data = {
        "customer_id": customer.id,
        f"checkpoint_{cp.id}_result": "OK",
        f"checkpoint_{cp.id}_comment": "Looks good",
        "finalize": "true"
    }
    response = client.post("/reports", data=data, follow_redirects=False)
    assert response.status_code == 303
    
    # 6. Verify original assignment is COMPLETED
    db.expire_all()
    updated_assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment.id).first()
    assert updated_assignment.status == models.AssignmentStatus.COMPLETED
    
    # 7. Verify new Recurring Assignment is created
    new_assignment = db.query(models.Assignment).filter(
        models.Assignment.customer_id == customer.id,
        models.Assignment.status == models.AssignmentStatus.PLANNED
    ).first()
    assert new_assignment is not None
    assert new_assignment.is_recurring is True
    
    # 8. Test Word Export
    report = db.query(models.Report).filter(models.Report.customer_id == customer.id).first()
    response = client.get(f"/reports/{report.id}/export")
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
    print("Cycle 2: Full flow test PASSED")

if __name__ == "__main__":
    try:
        test_full_lifecycle()
    except Exception as e:
        print(f"Cycle 2 test FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
