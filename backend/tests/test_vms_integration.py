"""Integration tests for VMS handoff and classification endpoints."""
import uuid


def test_classification_review_endpoint(client, db_session):
    """Test POST /api/v1/reviews/needs/{need_id}/classification endpoint."""
    from app.models.need import Need
    from datetime import UTC, datetime

    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-INT-001",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Call classification review endpoint
    response = client.post(
        f"/api/v1/reviews/needs/{need.id}/classification",
        json={
            "review_decision": "approve",
            "classification_verdict": "single_resource",
            "classification_confidence": 0.85,
            "rationale": "Clear single-resource case",
            "exemplars_referenced": ["EX-001"],
            "escalation_required": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["classification_verdict"] == "single_resource"
    assert data["next_workflow_status"] == "classified_single_resource"


def test_vms_handoff_endpoint(client, db_session):
    """Test POST /api/v1/integrations/vms/handoffs endpoint."""
    from app.models.need import Need
    from datetime import UTC, datetime

    # Create a classified single_resource need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-INT-002",
        channel_type="supplier_offer",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"contractor": "test"}',
        status="classified_single_resource",
        classification_verdict="single_resource",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Call VMS handoff endpoint
    response = client.post(
        "/api/v1/integrations/vms/handoffs",
        json={
            "need_id": str(need.id),
            "classification_verdict": "single_resource",
            "request_payload_json": {
                "contractor_name": "Jane Smith",
                "skill_set": "Cloud Architect",
            },
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["handover_confirmation"] is True
    assert data["vms_reference_id"] is not None
    assert data["workflow_status"] == "vms_routed_terminal"


def test_vms_handoff_rejects_it_service(client, db_session):
    """Test that VMS handoff rejects it_service needs."""
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-INT-003",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classified_it_service",
        classification_verdict="it_service",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    response = client.post(
        "/api/v1/integrations/vms/handoffs",
        json={
            "need_id": str(need.id),
            "classification_verdict": "it_service",
            "request_payload_json": {"test": "data"},
        },
    )

    # Pydantic validation rejects at request level
    assert response.status_code == 422


def test_classification_rejects_invalid_verdict(client, db_session):
    """Test that classification endpoint rejects invalid verdicts."""
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-INT-004",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Invalid verdict
    response = client.post(
        f"/api/v1/reviews/needs/{need.id}/classification",
        json={
            "review_decision": "approve",
            "classification_verdict": "invalid_type",
            "classification_confidence": 0.90,
        },
    )

    assert response.status_code == 422  # Pydantic validation error
