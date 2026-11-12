"""Integration tests for authentication endpoints."""
from app.models.user import User
from app.services.auth_service import hash_password


def test_login_success(client, db_session):
    """Test successful login with valid credentials."""
    # Create user
    user = User(
        email="user@example.com",
        username="testuser",
        hashed_password=hash_password("password123"),
        role="user",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "user@example.com"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["role"] == "user"


def test_login_invalid_credentials(client, db_session):
    """Test login with invalid credentials."""
    # Create user
    user = User(
        email="user@example.com",
        username="testuser",
        hashed_password=hash_password("password123"),
        role="user",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Try login with wrong password
    response = client.post("/api/v1/auth/login", json={
        "email": "user@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_nonexistent_user(client):
    """Test login with nonexistent user."""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_inactive_user(client, db_session):
    """Test login with inactive user."""
    # Create inactive user
    user = User(
        email="inactive@example.com",
        username="inactive",
        hashed_password=hash_password("password123"),
        role="user",
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    
    # Try login
    response = client.post("/api/v1/auth/login", json={
        "email": "inactive@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"].lower()


def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/api/v1/cases")
    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(auth_client):
    """Test accessing protected endpoint with valid token."""
    response = auth_client.get("/api/v1/cases")
    assert response.status_code == 200
