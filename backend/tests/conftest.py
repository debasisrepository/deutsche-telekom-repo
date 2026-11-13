import os
import tempfile
from datetime import datetime
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
os.environ["RATE_LIMIT_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Import all models to register them with Base
import app.models.audit_event  # noqa: F401
import app.models.classification_review  # noqa: F401
import app.models.longlist  # noqa: F401
import app.models.longlist_adjustment  # noqa: F401
import app.models.longlist_proposal  # noqa: F401
import app.models.longlist_ranked_supplier  # noqa: F401
import app.models.need  # noqa: F401
import app.models.need_attributes  # noqa: F401
import app.models.panel_match  # noqa: F401
import app.models.provider_candidate  # noqa: F401
import app.models.supplier_count_validation  # noqa: F401
import app.models.supplier_evidence_item  # noqa: F401
import app.models.tender_dispatch  # noqa: F401
import app.models.vms_handoff  # noqa: F401
from app.database import Base, get_db
from app.main import app

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
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client, db_session):
    """Logged in test client through the app's own login endpoint.
    
    Creates a procurement_reviewer user and authenticates via the real login endpoint.
    Tests of protected endpoints should use this fixture instead of bare `client`.
    """
    from app.core.security import hash_password
    from app.models.user import User

    # Create test user with procurement_reviewer role
    test_user = User(
        email="test_reviewer@example.com",
        hashed_password=hash_password("TestPass123!"),
        role="procurement_reviewer",
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()

    # Authenticate through real login endpoint
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test_reviewer@example.com", "password": "TestPass123!"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    
    if access_token:
        # Set Authorization header for subsequent requests
        client.headers["Authorization"] = f"Bearer {access_token}"
    
    return client


# Add pytest.now attribute for test timestamp
pytest.now = datetime.utcnow()
