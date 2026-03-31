import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role
from app.core.auth import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Clear existing users
    db.query(User).delete()
    
    # Admin user
    admin_user = User(
        username="beheerder",
        password_hash=get_password_hash("adminpass"),
        role=Role.ADMIN,
        is_active=True
    )
    # Technician user
    tech_user = User(
        username="technicus1",
        password_hash=get_password_hash("techpass"),
        role=Role.TECHNICUS,
        is_active=True
    )
    db.add_all([admin_user, tech_user])
    db.commit()
    yield db
    db.close()

def test_admin_login_redirect(setup_db):
    response = client.post("/login", data={"username": "beheerder", "password": "adminpass"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"

def test_technician_login_redirect(setup_db):
    response = client.post("/login", data={"username": "technicus1", "password": "techpass"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/behandelaar/dashboard"

def test_customers_admin_access(setup_db):
    # Log in as admin
    client.post("/login", data={"username": "beheerder", "password": "adminpass"})
    response = client.get("/customers/")
    assert response.status_code == 200

def test_customers_technician_access(setup_db):
    # Log in as technician
    client.post("/login", data={"username": "technicus1", "password": "techpass"})
    response = client.get("/customers/")
    # This should be forbidden once we implement require_admin
    assert response.status_code == 403
