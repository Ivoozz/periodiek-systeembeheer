import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role, Customer
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

def test_customers_list(auth_client, db_session: Session):
    c1 = Customer(name="Customer A", location="Loc A")
    db_session.add(c1)
    db_session.commit()
    
    response = auth_client.get("/customers")
    assert response.status_code == 200
    assert "Customer A" in response.text
    assert "Loc A" in response.text

def test_create_customer(auth_client, db_session: Session):
    response = auth_client.post("/customers", data={
        "name": "New Customer",
        "location": "New Loc",
        "contact_person": "Contact X"
    })
    assert response.status_code == 200
    # HTMX might return the new row or the updated list
    assert "New Customer" in response.text
    
    customer = db_session.query(Customer).filter(Customer.name == "New Customer").first()
    assert customer is not None

def test_search_customers(auth_client, db_session: Session):
    c1 = Customer(name="Apple", location="Loc A")
    c2 = Customer(name="Banana", location="Loc B")
    db_session.add_all([c1, c2])
    db_session.commit()
    
    response = auth_client.get("/customers?search=Apple")
    assert response.status_code == 200
    assert "Apple" in response.text
    assert "Banana" not in response.text

def test_delete_customer(auth_client, db_session: Session):
    c1 = Customer(name="To Delete", location="Loc D")
    db_session.add(c1)
    db_session.commit()
    
    customer_id = c1.id
    response = auth_client.delete(f"/customers/{customer_id}")
    assert response.status_code == 200
    
    customer = db_session.query(Customer).get(customer_id)
    assert customer is None
