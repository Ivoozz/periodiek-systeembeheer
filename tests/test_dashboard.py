import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role, Customer, Report
from app.core.auth import get_password_hash, create_session_cookie, SESSION_COOKIE_NAME

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

def test_dashboard_stats(auth_client, db_session: Session):
    # Add some data
    c1 = Customer(name="Customer 1", location="Location 1")
    c2 = Customer(name="Customer 2", location="Location 2")
    db_session.add_all([c1, c2])
    db_session.commit()
    
    response = auth_client.get("/dashboard")
    assert response.status_code == 200
    assert "Total Customers" in response.text
    assert "2" in response.text
    assert "Recent Reports" in response.text
