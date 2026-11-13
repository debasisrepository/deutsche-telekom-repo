"""Unit tests for PanelMappingService (ATS6)."""

import uuid
from datetime import UTC, datetime

import pytest

from app.models.need import Need
from app.services.panel_mapping_service import PanelMappingService


def test_map_need_to_panels_success(db_session):
    """Test successful panel mapping with multiple candidates."""
    # Create a test need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-001.pdf",
        normalized_payload_json='{"service": "cloud hosting"}',
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.95,
        correlation_id="test-corr-001",
    )
    db_session.add(need)
    db_session.commit()

    # Execute panel mapping
    service = PanelMappingService(db_session)
    response = service.map_need_to_panels(
        need_id=need.id,
        need_category="cloud_hosting",
        correlation_id="test-corr-001",
    )

    # Verify response structure
    assert response.need_id == need.id
    assert response.correlation_id == "test-corr-001"
    assert isinstance(response.candidate_suppliers, list)
    assert len(response.candidate_suppliers) > 0
    assert response.coverage_gap_flag is False

    # Verify candidate structure
    first_candidate = response.candidate_suppliers[0]
    assert first_candidate.panel_match_id is not None
    assert first_candidate.supplier_id is not None
    assert first_candidate.panel_source is not None
    assert first_candidate.functional_group is not None
    assert first_candidate.provenance_ref is not None


def test_map_need_to_panels_with_coverage_gap(db_session):
    """Test panel mapping detecting coverage gap for niche needs."""
    # Create a test need with niche category
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-002",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-002.pdf",
        normalized_payload_json='{"service": "specialized quantum computing"}',
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.88,
        correlation_id="test-corr-002",
    )
    db_session.add(need)
    db_session.commit()

    # Execute panel mapping with niche category
    service = PanelMappingService(db_session)
    response = service.map_need_to_panels(
        need_id=need.id,
        need_category="niche_quantum_computing",
        correlation_id="test-corr-002",
    )

    # Verify coverage gap detected
    assert response.coverage_gap_flag is True
    assert len(response.candidate_suppliers) >= 0  # May have limited candidates


def test_map_need_to_panels_need_not_found(db_session):
    """Test panel mapping with non-existent need."""
    service = PanelMappingService(db_session)

    with pytest.raises(ValueError, match="not found"):
        service.map_need_to_panels(
            need_id=uuid.uuid4(),
            need_category="cloud_hosting",
            correlation_id="test-corr-003",
        )


def test_map_need_to_panels_creates_audit_event(db_session):
    """Test that panel mapping creates audit event."""
    from app.models.audit_event import AuditEvent

    # Create a test need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-003",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-003.pdf",
        normalized_payload_json='{"service": "cloud hosting"}',
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.92,
        correlation_id="test-corr-004",
    )
    db_session.add(need)
    db_session.commit()

    # Execute panel mapping
    service = PanelMappingService(db_session)
    service.map_need_to_panels(
        need_id=need.id,
        need_category="cloud_hosting",
        correlation_id="test-corr-004",
    )

    # Verify audit event created
    audit_events = db_session.query(AuditEvent).filter(
        AuditEvent.need_id == need.id,
        AuditEvent.step_code == "ATS6",
    ).all()

    assert len(audit_events) == 1
    audit_event = audit_events[0]
    assert audit_event.correlation_id == "test-corr-004"
    assert audit_event.agent_code == "AGN2"
    assert audit_event.tool_code == "TOL3"
    assert audit_event.actor_type == "system"
