import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.db.models import User, Role
from app.core.auth import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # Make sure we are using a clean DB for tests or the default test db
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Clear users to be sure
    db.query(User).delete()
    # Create test user
    test_user = User(
        username="testuser",
        password_hash=get_password_hash("testpassword"),
        role=Role.ADMIN,
        is_active=True
    )
    db.add(test_user)
    db.commit()
    yield db
    db.close()
    # Base.metadata.drop_all(bind=engine) # Keep it for inspection if needed, or drop

def test_login_flow(test_db):
    # Test login page
    response = client.get("/login")
    assert response.status_code == 200
    assert "Login" in response.text

    # Test login failure
    response = client.post("/login", data={"username": "testuser", "password": "wrongpassword"}, follow_redirects=False)
    assert response.status_code == 303
    assert "/login?error=1" in response.headers["location"]

    # Test login success
    response = client.post("/login", data={"username": "testuser", "password": "testpassword"}, follow_redirects=False)
    assert response.status_code == 303
    assert "/dashboard" in response.headers["location"]
    assert "session" in client.cookies

    # Test logout
    response = client.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert "/login" in response.headers["location"]
    assert "session" not in client.cookies or client.cookies.get("session") == ""
