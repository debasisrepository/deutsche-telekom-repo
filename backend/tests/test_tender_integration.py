"""Integration tests for tender lock and dispatch endpoints."""

import json
import uuid
from datetime import UTC, datetime

from app.models.longlist import Longlist
from app.models.need import Need


def test_lock_longlist_endpoint(client, db_session):
    """Test POST /api/v1/longlists/{longlist_id}/lock endpoint."""
    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-artifact",
        normalized_payload_json="{}",
        status="classified_it_service",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Create an unlocked longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Lock the longlist
    response = client.post(
        f"/api/v1/longlists/{longlist.id}/lock",
        json={
            "expected_validation_verdict": "pass",
            "supplier_ids": ["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"],
            "finalized_by": "finalization_user",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["longlist_id"] == str(longlist.id)
    assert data["need_id"] == str(need.id)
    assert data["locked"] is True
    assert "locked_at" in data
    assert data["validation_count"] == 4


def test_dispatch_tender_endpoint(client, db_session):
    """Test POST /api/v1/tenders/dispatch endpoint."""
    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-artifact",
        normalized_payload_json="{}",
        status="classified_it_service",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Create a locked longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307"]),
        locked=True,
        locked_at=datetime.now(UTC),
        locked_by="finalization_user",
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Dispatch tender
    response = client.post(
        "/api/v1/tenders/dispatch",
        json={
            "longlist_id": str(longlist.id),
            "tender_template": "TEMPLATE-001",
            "supplier_contacts": [
                {"supplier_id": "SUP-0231", "contact_email": "contact1@example.com", "contact_name": "Contact 1"},
                {"supplier_id": "SUP-0118", "contact_email": "contact2@example.com", "contact_name": "Contact 2"},
                {"supplier_id": "SUP-0307", "contact_email": "contact3@example.com", "contact_name": "Contact 3"},
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "dispatch_batch_id" in data
    assert data["longlist_id"] == str(longlist.id)
    assert len(data["supplier_dispatches"]) == 3


def test_get_audit_events_endpoint(client, db_session):
    """Test GET /api/v1/workflows/{need_id}/audit-events endpoint."""
    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-artifact",
        normalized_payload_json="{}",
        status="classified_it_service",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Query audit events
    response = client.get(f"/api/v1/workflows/{need.id}/audit-events")

    assert response.status_code == 200
    data = response.json()
    assert data["need_id"] == str(need.id)
    assert "audit_events" in data
    assert "total_count" in data


def test_lock_longlist_validation_failure(client, db_session):
    """Test lock rejection when validation fails."""
    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-artifact",
        normalized_payload_json="{}",
        status="classified_it_service",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Create an unlocked longlist with 2 suppliers (below minimum)
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        suppliers=json.dumps(["SUP-0231", "SUP-0118"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Attempt to lock should fail
    response = client.post(
        f"/api/v1/longlists/{longlist.id}/lock",
        json={
            "expected_validation_verdict": "pass",
            "supplier_ids": ["SUP-0231", "SUP-0118"],
            "finalized_by": "finalization_user",
        },
    )

    assert response.status_code == 400
    assert "validation verdict is 'fail'" in response.json()["detail"]


def test_dispatch_tender_unlocked_longlist(client, db_session):
    """Test dispatch rejection when longlist not locked."""
    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-artifact",
        normalized_payload_json="{}",
        status="classified_it_service",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Create an unlocked longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Attempt dispatch should fail
    response = client.post(
        "/api/v1/tenders/dispatch",
        json={
            "longlist_id": str(longlist.id),
            "tender_template": "TEMPLATE-001",
            "supplier_contacts": [
                {"supplier_id": "SUP-0231", "contact_email": "contact1@example.com", "contact_name": "Contact 1"},
            ],
        },
    )

    assert response.status_code == 400
    assert "not locked" in response.json()["detail"]
