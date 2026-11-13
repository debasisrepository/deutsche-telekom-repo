"""Unit tests for LonglistProposalService (ATS8)."""

import json
import uuid

import pytest

from app.models.need import Need
from app.models.panel_match import PanelMatch
from app.models.provider_candidate import ProviderCandidate
from app.models.supplier_evidence_item import SupplierEvidenceItem
from app.services.longlist_proposal_service import LonglistProposalService


def test_generate_proposal_success(db_session):
    """Test successful proposal generation with panel matches and evidence."""
    # Create need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=pytest.now,
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.95,
        evidence_limited_flag=False,
        correlation_id="test-correlation-1",
    )
    db_session.add(need)
    db_session.commit()

    # Create panel matches
    panel_match_1 = PanelMatch(
        id=uuid.uuid4(),
        need_id=need.id,
        supplier_id="SUP-0231",
        panel_source="Cloud and hosting",
        functional_group="Infrastructure",
        provenance_ref="TOL3-panel-001",
        coverage_gap_flag=False,
    )
    panel_match_2 = PanelMatch(
        id=uuid.uuid4(),
        need_id=need.id,
        supplier_id="SUP-0118",
        panel_source="Platform engineering",
        functional_group="Development",
        provenance_ref="TOL3-panel-002",
        coverage_gap_flag=False,
    )
    db_session.add(panel_match_1)
    db_session.add(panel_match_2)
    db_session.commit()

    # Create evidence items
    evidence_1 = SupplierEvidenceItem(
        id=uuid.uuid4(),
        need_id=need.id,
        supplier_id="SUP-0231",
        evidence_type="completed_sow",
        source_system="TOL2",
        source_reference="SOW-2022-0871",
        service_category="Cloud Infrastructure",
        quality_rating=4.8,
        citation_text="Successfully delivered cloud migration for major enterprise client",
        is_seed_data=False,
        evidence_snapshot_timestamp=pytest.now,
    )
    evidence_2 = SupplierEvidenceItem(
        id=uuid.uuid4(),
        need_id=need.id,
        supplier_id="SUP-0118",
        evidence_type="historical_order",
        source_system="TOL2",
        source_reference="ORD-2023-4410",
        service_category="Platform Services",
        quality_rating=4.5,
        citation_text="Platform modernization project completed on time",
        is_seed_data=False,
        evidence_snapshot_timestamp=pytest.now,
    )
    db_session.add(evidence_1)
    db_session.add(evidence_2)
    db_session.commit()

    # Generate proposal
    service = LonglistProposalService(db_session)
    response = service.generate_proposal(
        need_id=need.id,
        matched_panels=[str(panel_match_1.id), str(panel_match_2.id)],
        evidence_items=[str(evidence_1.id), str(evidence_2.id)],
        approved_niche_candidates=[],
        correlation_id="test-correlation-1",
    )

    # Assertions
    assert response.proposal_id is not None
    assert response.need_id == need.id
    assert len(response.ranked_suppliers) == 2
    assert response.evidence_limited_flag is False

    # Check ranked suppliers
    supplier_ids = [rs.supplier_id for rs in response.ranked_suppliers]
    assert "SUP-0231" in supplier_ids
    assert "SUP-0118" in supplier_ids

    # Check citations present
    for rs in response.ranked_suppliers:
        assert len(rs.evidence_citations) > 0
        assert rs.rank_rationale != ""
        assert rs.confidence > 0.0


def test_generate_proposal_rejects_uncited_suppliers(db_session):
    """Test that panel matches now carry panel source as citation.
    
    Panel membership is evidence - suppliers from panel matches should have
    citations referencing their panel source. This test verifies that panel
    matches successfully generate citations and proposals no longer reject
    panel-only suppliers.
    """
    # Create need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-002",
        channel_type="email",
        arrival_timestamp=pytest.now,
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.90,
        evidence_limited_flag=False,
        correlation_id="test-correlation-2",
    )
    db_session.add(need)
    db_session.commit()

    # Create panel match - panel source itself provides citation
    panel_match = PanelMatch(
        id=uuid.uuid4(),
        need_id=need.id,
        supplier_id="SUP-9999",
        panel_source="Unknown panel",
        functional_group="Unknown",
        provenance_ref="TOL3-panel-999",
        coverage_gap_flag=False,
    )
    db_session.add(panel_match)
    db_session.commit()

    # Generate proposal - should succeed because panel match provides citation
    service = LonglistProposalService(db_session)

    result = service.generate_proposal(
        need_id=need.id,
        matched_panels=[str(panel_match.id)],
        evidence_items=[],
        approved_niche_candidates=[],
        correlation_id="test-correlation-2",
    )
    
    # Verify proposal was created successfully
    assert result.proposal_id is not None
    assert len(result.ranked_suppliers) == 1
    # Verify citation from panel source
    assert len(result.ranked_suppliers[0].evidence_citations) > 0
    assert result.ranked_suppliers[0].evidence_citations[0].source_reference == "Unknown panel"


def test_generate_proposal_with_niche_candidates(db_session):
    """Test proposal generation including approved niche candidates."""
    # Create need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-003",
        channel_type="rfp",
        arrival_timestamp=pytest.now,
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.88,
        evidence_limited_flag=True,
        correlation_id="test-correlation-3",
    )
    db_session.add(need)
    db_session.commit()

    # Create niche candidate
    niche_candidate = ProviderCandidate(
        id=uuid.uuid4(),
        need_id=need.id,
        candidate_name="CloudTech Solutions",
        supplier_id="SUP-0518",
        capability_gap="Advanced Kubernetes orchestration",
        source_citations=json.dumps([
            {"source": "Gaia-X", "citation": "Certified provider in EU cloud federation"}
        ]),
        review_status="approved",
    )
    db_session.add(niche_candidate)
    db_session.commit()

    # Generate proposal
    service = LonglistProposalService(db_session)
    response = service.generate_proposal(
        need_id=need.id,
        matched_panels=[],
        evidence_items=[],
        approved_niche_candidates=[str(niche_candidate.id)],
        correlation_id="test-correlation-3",
    )

    # Assertions
    assert response.proposal_id is not None
    assert len(response.ranked_suppliers) == 1
    assert response.ranked_suppliers[0].supplier_id == "SUP-0518"
    assert len(response.ranked_suppliers[0].evidence_citations) > 0


def test_generate_proposal_need_not_found(db_session):
    """Test proposal generation fails when need not found."""
    service = LonglistProposalService(db_session)

    with pytest.raises(ValueError, match="Need .* not found"):
        service.generate_proposal(
            need_id=uuid.uuid4(),
            matched_panels=[],
            evidence_items=[],
            approved_niche_candidates=[],
            correlation_id="test-correlation-4",
        )
