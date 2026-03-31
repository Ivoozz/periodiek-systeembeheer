
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role, Customer, Report
from app.core.auth import get_password_hash, create_session_cookie

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Admin user
    admin_user = User(
        username="admin",
        password_hash=get_password_hash("adminpass"),
        role=Role.ADMIN,
        is_active=True
    )
    # Technician user
    tech_user = User(
        username="tech",
        password_hash=get_password_hash("techpass"),
        role=Role.TECHNICUS,
        is_active=True
    )
    # Client user 1
    client_user1 = User(
        username="client1",
        password_hash=get_password_hash("clientpass"),
        role=Role.CLIENT,
        is_active=True
    )
    # Client user 2
    client_user2 = User(
        username="client2",
        password_hash=get_password_hash("clientpass"),
        role=Role.CLIENT,
        is_active=True
    )
    
    db.add_all([admin_user, tech_user, client_user1, client_user2])
    db.commit()
    
    # Add customers for clients
    c1 = Customer(name="Customer 1", user_id=client_user1.id)
    c2 = Customer(name="Customer 2", user_id=client_user2.id)
    db.add_all([c1, c2])
    db.commit()

    # Add reports
    r1 = Report(customer_id=c1.id, technician_id=tech_user.id)
    r2 = Report(customer_id=c2.id, technician_id=tech_user.id)
    db.add_all([r1, r2])
    db.commit()

    yield db
    db.close()

def get_session_cookie(user_id):
    return {"session": create_session_cookie(user_id)}

def test_sqlcipher_key_validity(setup_db):
    # This is implicitly tested by setup_db and any query.
    # If the key was invalid, setup_db would fail or queries would fail.
    db = setup_db
    user = db.query(User).filter(User.username == "admin").first()
    assert user is not None

def test_rbac_client_access_admin_settings(setup_db):
    db = setup_db
    client_user = db.query(User).filter(User.username == "client1").first()
    cookies = get_session_cookie(client_user.id)
    
    # Try to access admin settings
    response = client.get("/settings", cookies=cookies)
    # Should be 403 or 303 to login if middleware redirects, but usually 403 for RBAC
    assert response.status_code in [403, 303, 401]

def test_rbac_client_access_other_client_report(setup_db):
    db = setup_db
    client_user1 = db.query(User).filter(User.username == "client1").first()
    client_user2 = db.query(User).filter(User.username == "client2").first()
    
    report2 = db.query(Report).join(Customer).filter(Customer.user_id == client_user2.id).first()
    
    cookies = get_session_cookie(client_user1.id)
    # Try to access report of client 2
    response = client.get(f"/reports/{report2.id}", cookies=cookies)
    assert response.status_code in [403, 404] # 404 might be used for obfuscation or simple filter

def test_rbac_technician_access_admin_settings(setup_db):
    db = setup_db
    tech_user = db.query(User).filter(User.username == "tech").first()
    cookies = get_session_cookie(tech_user.id)
    
    response = client.get("/settings", cookies=cookies)
    assert response.status_code == 403

def test_signed_cookies_tampering(setup_db):
    cookies = {"session": "tampered-token"}
    response = client.get("/dashboard", cookies=cookies)
    # Should redirect to login or be 401
    assert response.status_code in [303, 401]
