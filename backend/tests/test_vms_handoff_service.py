"""Unit tests for VmsHandoffService."""
import uuid

import pytest

from app.services.vms_handoff_service import VmsHandoffService
from app.schemas.vms_schemas import VmsHandoffRequest


def test_successful_vms_handoff(db_session):
    """Test successful VMS handoff for single_resource need."""
    from app.models.need import Need
    from datetime import UTC, datetime

    # Create a single_resource need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-VMS-001",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="vms-test",
        normalized_payload_json='{"contractor_type": "single_resource"}',
        status="classified_single_resource",
        classification_verdict="single_resource",
        classification_confidence=0.88,
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Execute handoff
    request = VmsHandoffRequest(
        need_id=need.id,
        classification_verdict="single_resource",
        request_payload_json={
            "contractor_name": "John Doe",
            "skill_set": "Python Developer",
            "duration": "6 months",
        },
    )

    service = VmsHandoffService(db_session)
    response = service.execute_handoff(request)

    # Assertions
    assert response.need_id == need.id
    assert response.handover_confirmation is True
    assert response.vms_reference_id is not None
    assert response.vms_reference_id.startswith("VMS-")
    assert response.workflow_status == "vms_routed_terminal"

    # Verify need status updated
    db_session.refresh(need)
    assert need.status == "vms_routed_terminal"


def test_vms_handoff_requires_single_resource_verdict(db_session):
    """Test that VMS handoff rejects non-single_resource verdicts."""
    from pydantic import ValidationError

    # Try to handoff it_service - should fail at Pydantic validation
    with pytest.raises(ValidationError, match="classification_verdict"):
        VmsHandoffRequest(
            need_id=uuid.uuid4(),
            classification_verdict="it_service",
            request_payload_json={"test": "data"},
        )


def test_vms_handoff_requires_correct_workflow_status(db_session):
    """Test that VMS handoff requires classified_single_resource status."""
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-VMS-003",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test",
        normalized_payload_json='{"test": "data"}',
        status="normalized",  # Wrong status
        classification_verdict="single_resource",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    request = VmsHandoffRequest(
        need_id=need.id,
        classification_verdict="single_resource",
        request_payload_json={"test": "data"},
    )

    service = VmsHandoffService(db_session)

    with pytest.raises(ValueError, match="Expected classified_single_resource"):
        service.execute_handoff(request)


def test_vms_handoff_blocks_ats5_12_workflow(db_session):
    """Test that VMS handoff marks workflow as terminal, blocking ATS5-ATS12."""
    from app.models.need import Need
    from datetime import UTC, datetime

    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-VMS-004",
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

    request = VmsHandoffRequest(
        need_id=need.id,
        classification_verdict="single_resource",
        request_payload_json={"contractor": "test"},
    )

    service = VmsHandoffService(db_session)
    response = service.execute_handoff(request)

    # Terminal status blocks ATS5-ATS12
    assert response.workflow_status == "vms_routed_terminal"

    db_session.refresh(need)
    assert need.status == "vms_routed_terminal"
