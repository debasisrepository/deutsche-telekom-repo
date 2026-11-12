import os
import tempfile
from pathlib import Path

# 1. Configuration BEFORE anything imports the app: the committed dev.env, then test overrides.
_BACKEND = Path(__file__).resolve().parents[1]
for _seed in ("dev.env", ".env.example"):
    if (_BACKEND / _seed).is_file():
        for _line in (_BACKEND / _seed).read_text().splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _value = _line.removeprefix("export ").split("=", 1)
                os.environ.setdefault(_key.strip(), _value.strip().strip("\"'"))
        break
_DB_FILE = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_FILE.as_posix()}"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401 - registers every model on Base before create_all
from app.database import Base, get_db
from app.main import app as fastapi_app

engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session() -> Session:
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Test user fixture for workflow tests."""
    from app.models.user import User
    from app.services.auth_service import hash_password
    
    user = User(
        email="tester@example.com",
        username="tester",
        hashed_password=hash_password("Test-pass-1"),
        role="user",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def auth_client(client, test_user):
    """Logged in client through the app's own login."""
    # Login
    response = client.post("/api/v1/auth/login", json={"email": "tester@example.com", "password": "Test-pass-1"})
    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    
    if token:
        client.headers["Authorization"] = f"Bearer {token}"
    
    return client
