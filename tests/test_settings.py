import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role, WhitelabelSettings, Customer
from app.core.auth import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Clear existing data
    db.query(User).delete()
    db.query(WhitelabelSettings).delete()
    db.query(Customer).delete()
    db.commit()
    
    # Admin user
    admin_user = User(
        username="admin_task4",
        password_hash=get_password_hash("adminpass"),
        role=Role.ADMIN,
        is_active=True
    )
    # Technician user
    tech_user = User(
        username="tech_task4",
        password_hash=get_password_hash("techpass"),
        role=Role.TECHNICUS,
        is_active=True
    )
    # Client user
    client_user = User(
        username="client_task4",
        password_hash=get_password_hash("clientpass"),
        role=Role.CLIENT,
        is_active=True
    )
    db.add_all([admin_user, tech_user, client_user])
    db.commit()
    
    # Create customer linked to client
    customer = Customer(
        name="Test Customer",
        contact_name="Old Name",
        contact_phone="000",
        user_id=client_user.id
    )
    # Another customer NOT linked to client
    other_customer = Customer(
        name="Other Customer",
        contact_name="Other Name",
        contact_phone="111",
        user_id=None
    )
    db.add_all([customer, other_customer])
    db.commit()
    
    yield db
    db.close()

def test_admin_settings_access_admin(setup_db):
    client.post("/login", data={"username": "admin_task4", "password": "adminpass"})
    response = client.get("/admin/settings")
    assert response.status_code == 200

def test_admin_settings_access_tech(setup_db):
    client.post("/login", data={"username": "tech_task4", "password": "techpass"})
    response = client.get("/admin/settings")
    assert response.status_code == 403

def test_admin_settings_update(setup_db):
    client.post("/login", data={"username": "admin_task4", "password": "adminpass"})
    response = client.post("/admin/settings", data={
        "brand_name": "New Brand",
        "logo_url": "http://logo.png",
        "primary_color": "#ff0000",
        "secondary_color": "#00ff00"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/settings"
    
    # Verify in DB
    db = SessionLocal()
    settings = db.query(WhitelabelSettings).first()
    assert settings.brand_name == "New Brand"
    assert settings.primary_color == "#ff0000"
    db.close()

def test_update_customer_contact_admin(setup_db):
    db = SessionLocal()
    customer = db.query(Customer).filter(Customer.name == "Test Customer").first()
    customer_id = customer.id
    db.close()
    
    client.post("/login", data={"username": "admin_task4", "password": "adminpass"})
    response = client.post(f"/customers/{customer_id}/contact", data={
        "contact_name": "Admin Updated",
        "contact_phone": "12345"
    }, follow_redirects=False)
    assert response.status_code == 303
    
    db = SessionLocal()
    customer = db.query(Customer).get(customer_id)
    assert customer.contact_name == "Admin Updated"
    db.close()

def test_update_customer_contact_client_own(setup_db):
    db = SessionLocal()
    customer = db.query(Customer).filter(Customer.name == "Test Customer").first()
    customer_id = customer.id
    db.close()
    
    client.post("/login", data={"username": "client_task4", "password": "clientpass"})
    response = client.post(f"/customers/{customer_id}/contact", data={
        "contact_name": "Client Updated",
        "contact_phone": "67890"
    }, follow_redirects=False)
    assert response.status_code == 303
    
    db = SessionLocal()
    customer = db.query(Customer).get(customer_id)
    assert customer.contact_name == "Client Updated"
    db.close()

def test_update_customer_contact_client_other(setup_db):
    db = SessionLocal()
    customer = db.query(Customer).filter(Customer.name == "Other Customer").first()
    customer_id = customer.id
    db.close()
    
    client.post("/login", data={"username": "client_task4", "password": "clientpass"})
    response = client.post(f"/customers/{customer_id}/contact", data={
        "contact_name": "Hack Attempt",
        "contact_phone": "999"
    })
    assert response.status_code == 403
