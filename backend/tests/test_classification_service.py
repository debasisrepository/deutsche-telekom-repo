"""Unit tests for ClassificationDecisionService."""
import uuid

import pytest

from app.services.classification_decision_service import ClassificationDecisionService
from app.schemas.vms_schemas import ClassificationReviewRequest


def test_approve_single_resource_classification(db_session):
    """Test approve decision for single_resource classification."""
    from app.models.need import Need
    from datetime import UTC, datetime

    # Create a need in classification_review_pending state
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-TEST-001",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-artifact",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Create classification review request
    request = ClassificationReviewRequest(
        review_decision="approve",
        classification_verdict="single_resource",
        classification_confidence=0.85,
        rationale="Clear single-resource need based on scope",
        exemplars_referenced=["EX-001", "EX-002"],
        escalation_required=False,
    )

    # Execute service
    service = ClassificationDecisionService(db_session)
    response = service.review_classification(need.id, request, "reviewer@example.com")

    # Assertions
    assert response.need_id == need.id
    assert response.review_decision == "approve"
    assert response.classification_verdict == "single_resource"
    assert response.classification_confidence == 0.85
    assert response.next_workflow_status == "classified_single_resource"
    assert response.escalation_required is False

    # Verify need updated
    db_session.refresh(need)
    assert need.classification_verdict == "single_resource"
    assert need.status == "classified_single_resource"


def test_approve_it_service_classification(db_session):
    """Test approve decision for it_service classification."""
    from app.models.need import Need
    from datetime import UTC, datetime

    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-TEST-002",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-rfp",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    request = ClassificationReviewRequest(
        review_decision="approve",
        classification_verdict="it_service",
        classification_confidence=0.92,
        rationale="Complex IT service requiring longlist",
        exemplars_referenced=["EX-010"],
        escalation_required=False,
    )

    service = ClassificationDecisionService(db_session)
    response = service.review_classification(need.id, request, "reviewer@example.com")

    assert response.classification_verdict == "it_service"
    assert response.next_workflow_status == "classified_it_service"

    db_session.refresh(need)
    assert need.status == "classified_it_service"


def test_low_confidence_triggers_escalation(db_session):
    """Test that low confidence automatically triggers escalation."""
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-TEST-003",
        channel_type="phone",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-phone",
        normalized_payload_json='{"test": "data"}',
        status="classification_review_pending",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Low confidence (below 0.70 threshold)
    request = ClassificationReviewRequest(
        review_decision="approve",
        classification_verdict="it_service",
        classification_confidence=0.65,
        rationale="Borderline case",
        escalation_required=False,  # Will be overridden
    )

    service = ClassificationDecisionService(db_session)
    response = service.review_classification(need.id, request, "reviewer@example.com")

    # Should trigger escalation and hold in review pending
    assert response.escalation_required is True
    assert response.next_workflow_status == "classification_review_pending"

    db_session.refresh(need)
    assert need.status == "classification_review_pending"


def test_invalid_verdict_rejected(db_session):
    """Test that invalid classification verdicts are rejected."""
    from pydantic import ValidationError

    # Invalid verdict - should fail at Pydantic validation
    with pytest.raises(ValidationError, match="classification_verdict"):
        ClassificationReviewRequest(
            review_decision="approve",
            classification_verdict="other_type",  # Invalid
            classification_confidence=0.90,
            rationale="Test",
        )
