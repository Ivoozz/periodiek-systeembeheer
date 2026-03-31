import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_secure_headers():
    response = client.get("/")
    headers = response.headers
    
    assert "Strict-Transport-Security" in headers
    assert "Content-Security-Policy" in headers
    assert "X-Frame-Options" in headers
    assert "X-Content-Type-Options" in headers
    assert "Referrer-Policy" in headers
    
    assert headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

def test_rate_limiting_login():
    # We'll assume the rate limit is 5 requests per minute
    # Resetting state by using a new client might not work if the state is in a global variable
    # But since it's a new test process, it should be fine.
    
    # First 5 should be 200 OK
    for i in range(5):
        response = client.get("/login")
        assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}"
    
    # The 6th should be 429
    response = client.get("/login")
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}
