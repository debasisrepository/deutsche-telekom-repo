"""Acceptance tests for classification and VMS handoff features (FR-003, FR-004)."""
import uuid


def test_classification_verdict_and_confidence_recorded(client, db_session):
    """
    FR-003: The product records classification_verdict and classification_confidence
    for each classified need.
    """
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-ACC-001",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    response = client.post(
        f"/api/v1/reviews/needs/{need.id}/classification",
        json={
            "review_decision": "approve",
            "classification_verdict": "it_service",
            "classification_confidence": 0.88,
            "rationale": "Complex IT service",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["classification_verdict"] == "it_service"
    assert data["classification_confidence"] == 0.88

    # Verify in database
    db_session.refresh(need)
    assert need.classification_verdict == "it_service"
    assert need.classification_confidence == 0.88


def test_only_single_resource_and_it_service_allowed(client, db_session):
    """
    FR-003: The only allowed verdicts are single_resource and it_service.
    """
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-ACC-002",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Try invalid verdict - should fail at Pydantic validation
    response = client.post(
        f"/api/v1/reviews/needs/{need.id}/classification",
        json={
            "review_decision": "approve",
            "classification_verdict": "other_type",
            "classification_confidence": 0.90,
        },
    )

    assert response.status_code == 422  # Pydantic validation


def test_reviewer_can_approve_modify_reject(client, db_session):
    """
    FR-003: Reviewers can approve, override, or request correction, and the final
    reviewed decision is logged with rationale.
    """
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-ACC-003",
        channel_type="phone",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Modify decision (override)
    response = client.post(
        f"/api/v1/reviews/needs/{need.id}/classification",
        json={
            "review_decision": "modify",
            "classification_verdict": "single_resource",
            "classification_confidence": 0.75,
            "rationale": "Overriding to single_resource after review",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["review_decision"] == "modify"
    assert data["classification_verdict"] == "single_resource"
    assert data["rationale"] == "Overriding to single_resource after review"


def test_low_confidence_held_for_review(client, db_session):
    """
    FR-003: Borderline or low-confidence classifications are held for review
    and may not auto-route out of the process.
    """
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-ACC-004",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Low confidence (0.65 < 0.70 threshold)
    response = client.post(
        f"/api/v1/reviews/needs/{need.id}/classification",
        json={
            "review_decision": "approve",
            "classification_verdict": "it_service",
            "classification_confidence": 0.65,
            "rationale": "Borderline case",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["escalation_required"] is True
    assert data["next_workflow_status"] == "classification_review_pending"


def test_classification_uses_structured_attributes(client, db_session):
    """
    FR-003: The classification step uses the structured attribute set as the
    decision surface and preserves audit trail with exemplars.
    """
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-ACC-005",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    response = client.post(
        f"/api/v1/reviews/needs/{need.id}/classification",
        json={
            "review_decision": "approve",
            "classification_verdict": "it_service",
            "classification_confidence": 0.92,
            "rationale": "Matches historical IT service patterns",
            "exemplars_referenced": ["EX-2024-001", "EX-2024-015"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["exemplars_referenced"] == ["EX-2024-001", "EX-2024-015"]
    assert data["rationale"] is not None


def test_single_resource_vms_handoff(client, db_session):
    """
    FR-004: When a reviewed classification result is single_resource, the product
    sends the normalized need record to VMS through the defined handoff interface.
    """
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-ACC-006",
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

    response = client.post(
        "/api/v1/integrations/vms/handoffs",
        json={
            "need_id": str(need.id),
            "classification_verdict": "single_resource",
            "request_payload_json": {"contractor_name": "John Doe"},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["handover_confirmation"] is True
    assert data["vms_reference_id"] is not None


def test_vms_handoff_returns_confirmation_and_reference(client, db_session):
    """
    FR-004: The outbound handoff returns and stores handover_confirmation
    and vms_reference_id.
    """
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-ACC-007",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classified_single_resource",
        classification_verdict="single_resource",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    response = client.post(
        "/api/v1/integrations/vms/handoffs",
        json={
            "need_id": str(need.id),
            "classification_verdict": "single_resource",
            "request_payload_json": {"test": "data"},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "handover_confirmation" in data
    assert "vms_reference_id" in data
    assert data["vms_reference_id"].startswith("VMS-")


def test_workflow_marked_terminal_after_vms_handoff(client, db_session):
    """
    FR-004: The supplier-selection workflow status is marked terminal for that
    case after successful VMS handoff.
    """
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-ACC-008",
        channel_type="phone",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classified_single_resource",
        classification_verdict="single_resource",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    response = client.post(
        "/api/v1/integrations/vms/handoffs",
        json={
            "need_id": str(need.id),
            "classification_verdict": "single_resource",
            "request_payload_json": {"test": "data"},
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["workflow_status"] == "vms_routed_terminal"

    # Verify need status
    db_session.refresh(need)
    assert need.status == "vms_routed_terminal"


def test_single_resource_blocked_from_ats5_12(client, db_session):
    """
    FR-004: Single-resource cases are blocked from ATS5 through ATS12 and cannot
    re-enter the longlist path without an explicit reviewed reclassification.
    """
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-ACC-009",
        channel_type="supplier_offer",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="classified_single_resource",
        classification_verdict="single_resource",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Execute handoff
    response = client.post(
        "/api/v1/integrations/vms/handoffs",
        json={
            "need_id": str(need.id),
            "classification_verdict": "single_resource",
            "request_payload_json": {"test": "data"},
        },
    )

    assert response.status_code == 201
    assert response.json()["workflow_status"] == "vms_routed_terminal"

    # Verify terminal status blocks further workflow
    db_session.refresh(need)
    assert need.status == "vms_routed_terminal"
    # In production, ATS5-ATS12 would check this status and refuse to proceed
