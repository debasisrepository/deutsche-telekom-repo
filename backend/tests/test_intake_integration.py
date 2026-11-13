"""Integration tests for intake API."""
import uuid


def test_create_need_endpoint(client):
    """Test POST /api/v1/intake/needs endpoint."""
    payload = {
        "business_unit_id": "BU-TEST-001",
        "channel_type": "rfp",
        "raw_artifact_ref": "test-rfp.pdf",
        "normalized_payload_json": '{"title": "Test RFP"}',
    }
    
    response = client.post(
        "/api/v1/intake/needs",
        json=payload,
        headers={"X-Correlation-Id": "integration-test-001"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "need_id" in data
    assert data["status"] == "normalized"
    assert data["correlation_id"] == "integration-test-001"


def test_create_need_invalid_channel(client):
    """Test intake rejects invalid channel types."""
    payload = {
        "business_unit_id": "BU-TEST-002",
        "channel_type": "invalid",
    }
    
    response = client.post("/api/v1/intake/needs", json=payload)
    
    assert response.status_code == 422  # Validation error


def test_get_need_endpoint(client, db_session):
    """Test GET /api/v1/intake/needs/{need_id} endpoint."""
    # Create a need first
    from app.models.need import Need
    from datetime import UTC, datetime
    
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-GET-001",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="email-001.eml",
        normalized_payload_json='{"subject": "Request"}',
        status="normalized",
        correlation_id="get-test-001",
    )
    db_session.add(need)
    db_session.commit()
    
    # Retrieve it
    response = client.get(f"/api/v1/intake/needs/{need.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(need.id)
    assert data["business_unit_id"] == "BU-GET-001"
    assert data["channel_type"] == "email"
    assert data["status"] == "normalized"


def test_get_need_not_found(client):
    """Test GET returns 404 for non-existent need."""
    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/intake/needs/{fake_id}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_needs_endpoint(client, db_session):
    """Test GET /api/v1/intake/needs returns list of needs."""
    # Create some test needs
    from app.models.need import Need
    from datetime import UTC, datetime, timedelta

    now = datetime.now(UTC)
    need1 = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=now,
        raw_artifact_ref="ref1",
        normalized_payload_json='{"data": "test1"}',
        status="normalized",
        correlation_id="corr1",
    )
    need2 = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-002",
        channel_type="email",
        arrival_timestamp=now - timedelta(hours=1),
        raw_artifact_ref="ref2",
        normalized_payload_json='{"data": "test2"}',
        status="normalized",
        correlation_id="corr2",
    )
    db_session.add_all([need1, need2])
    db_session.commit()

    # Test list endpoint
    response = client.get("/api/v1/intake/needs")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # Verify needs are ordered by arrival_timestamp descending (newest first)
    need_ids = [str(need1.id), str(need2.id)]
    returned_ids = [n["id"] for n in data]
    assert str(need1.id) in returned_ids
    assert str(need2.id) in returned_ids

    # Verify first need has most recent timestamp
    first_need = data[0]
    assert "business_unit_id" in first_need
    assert "channel_type" in first_need
    assert "status" in first_need
