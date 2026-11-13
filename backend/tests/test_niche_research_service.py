"""Unit tests for NicheResearchService (ATS7)."""

import uuid
from datetime import UTC, datetime

import pytest

from app.models.need import Need
from app.services.niche_research_service import NicheResearchService


def test_research_niche_providers_success(db_session):
    """Test successful niche provider research."""
    # Create a test need classified as it_service
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-001.pdf",
        normalized_payload_json='{"service": "specialized hosting"}',
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.87,
        correlation_id="test-corr-001",
    )
    db_session.add(need)
    db_session.commit()

    # Execute niche research
    service = NicheResearchService(db_session)
    response = service.research_niche_providers(
        need_id=need.id,
        capability_gap="Specialized quantum-resistant encryption",
        approved_source_list=["Gaia-X participant registry", "BSI C5 attestation"],
        correlation_id="test-corr-001",
    )

    # Verify response structure
    assert response.need_id == need.id
    assert response.correlation_id == "test-corr-001"
    assert response.review_required is True
    assert isinstance(response.niche_research_dossier, list)
    assert len(response.niche_research_dossier) > 0

    # Verify dossier item structure
    first_item = response.niche_research_dossier[0]
    assert first_item.provider_candidate_id is not None
    assert first_item.candidate_name is not None
    assert first_item.supplier_id is not None
    assert first_item.capability_gap == "Specialized quantum-resistant encryption"
    assert isinstance(first_item.source_citations, list)
    assert len(first_item.source_citations) > 0
    assert first_item.review_status == "pending"


def test_research_niche_providers_need_not_found(db_session):
    """Test niche research with non-existent need."""
    service = NicheResearchService(db_session)

    with pytest.raises(ValueError, match="not found"):
        service.research_niche_providers(
            need_id=uuid.uuid4(),
            capability_gap="Some gap",
            approved_source_list=["Gaia-X"],
            correlation_id="test-corr-002",
        )


def test_research_niche_providers_wrong_classification(db_session):
    """Test niche research with non-it_service need."""
    # Create a need classified as single_resource
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-002",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-002.pdf",
        normalized_payload_json='{"service": "contractor"}',
        status="classified_single_resource",
        classification_verdict="single_resource",
        classification_confidence=0.95,
        correlation_id="test-corr-003",
    )
    db_session.add(need)
    db_session.commit()

    service = NicheResearchService(db_session)

    with pytest.raises(ValueError, match="it_service"):
        service.research_niche_providers(
            need_id=need.id,
            capability_gap="Some gap",
            approved_source_list=["Gaia-X"],
            correlation_id="test-corr-003",
        )


def test_research_niche_providers_no_approved_sources(db_session):
    """Test niche research without approved sources."""
    # Create a test need classified as it_service
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-003",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-003.pdf",
        normalized_payload_json='{"service": "specialized hosting"}',
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.87,
        correlation_id="test-corr-004",
    )
    db_session.add(need)
    db_session.commit()

    service = NicheResearchService(db_session)

    with pytest.raises(ValueError, match="approved_source_list"):
        service.research_niche_providers(
            need_id=need.id,
            capability_gap="Some gap",
            approved_source_list=[],
            correlation_id="test-corr-004",
        )


def test_research_niche_providers_creates_audit_event(db_session):
    """Test that niche research creates audit event."""
    from app.models.audit_event import AuditEvent

    # Create a test need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-004",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-004.pdf",
        normalized_payload_json='{"service": "specialized hosting"}',
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.90,
        correlation_id="test-corr-005",
    )
    db_session.add(need)
    db_session.commit()

    # Execute niche research
    service = NicheResearchService(db_session)
    service.research_niche_providers(
        need_id=need.id,
        capability_gap="Advanced security",
        approved_source_list=["Gaia-X", "BSI C5"],
        correlation_id="test-corr-005",
    )

    # Verify audit event created
    audit_events = db_session.query(AuditEvent).filter(
        AuditEvent.need_id == need.id,
        AuditEvent.step_code == "ATS7",
    ).all()

    assert len(audit_events) == 1
    audit_event = audit_events[0]
    assert audit_event.correlation_id == "test-corr-005"
    assert audit_event.agent_code == "AGN2"
    assert audit_event.actor_type == "system"
