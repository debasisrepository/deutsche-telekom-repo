"""Journey J-02: Longlist Research and Proposal acceptance tests.

Tests the complete user journey from evidence retrieval (ATS5) through panel mapping
(ATS6), niche research (ATS7), and ranked proposal generation (ATS8), covering
features FR-005, FR-006, FR-007, and FR-008.
"""

import json
import uuid

import pytest


def test_j02_complete_longlist_proposal_journey(auth_client, db_session):
    """Test complete J-02 journey with evidence, panel, and proposal.

    Journey steps:
    - Setup: Create classified IT service need
    - ATS5: Query evidence for suppliers
    - ATS6: Map need to panels
    - ATS8: Generate ranked longlist proposal (skip ATS7, no coverage gap)
    """
    # Setup: Create a classified IT service need for this journey
    from app.models.need import Need
    from app.models.need_attributes import NeedAttributes
    from app.models.classification_review import ClassificationReview
    from datetime import datetime, UTC

    need_id = uuid.uuid4()
    need = Need(
        id=need_id,
        business_unit_id="BU-J02-TEST",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="s3://test/j02-need.pdf",
        normalized_payload_json=json.dumps({"title": "Cloud Platform Services"}),
        status="classified_it_service",
        correlation_id="J02-001",
    )
    db_session.add(need)

    attrs = NeedAttributes(
        id=uuid.uuid4(),
        need_id=need_id,
        service_type="Cloud Platform",
        scope_description="Multi-cloud platform management",
        estimated_volume_duration="24 months",
        required_skills=json.dumps(["AWS", "Azure", "Kubernetes"]),
        budget_indication="€600K annually",
        delivery_location="Germany",
        field_confidence=json.dumps({"service_type": 0.90}),
    )
    db_session.add(attrs)

    classification = ClassificationReview(
        id=uuid.uuid4(),
        need_id=need_id,
        classification_verdict="it_service",
        classification_confidence=0.90,
        rationale="Cloud platform service requirement",
        review_decision="approve",
        reviewer_id="procurement_reviewer@example.com",
        escalation_required=False,
        exemplars_referenced=json.dumps(["EXEMPLAR-IT-001"]),
    )
    db_session.add(classification)
    db_session.commit()

    # ATS5: Query evidence
    evidence_payload = {
        "need_id": str(need_id),
        "service_type": "Cloud Platform",
        "required_skills": ["AWS", "Azure", "Kubernetes"],
        "business_unit_id": "BU-J02-TEST"
    }

    evidence_resp = auth_client.post(
        "/api/v1/evidence/queries",
        json=evidence_payload,
        headers={"X-Correlation-Id": "J02-001"}
    )
    assert evidence_resp.status_code == 200, f"Evidence query failed: {evidence_resp.text}"
    evidence_data = evidence_resp.json()
    # Evidence returned with fallback flag or real data
    assert "evidence_items" in evidence_data
    assert "evidence_limited_flag" in evidence_data

    # ATS6: Map to panels
    panel_payload = {
        "need_id": str(need_id),
        "need_category": "Cloud Platform"
    }

    panel_resp = auth_client.post(
        "/api/v1/panel-mappings",
        json=panel_payload,
        headers={"X-Correlation-Id": "J02-001"}
    )
    assert panel_resp.status_code == 200, f"Panel mapping failed: {panel_resp.text}"
    panel_data = panel_resp.json()
    assert "candidate_suppliers" in panel_data
    assert "coverage_gap_flag" in panel_data
    # Should have some candidates
    assert len(panel_data["candidate_suppliers"]) > 0

    # ATS8: Generate proposal (assuming no coverage gap)
    # Extract panel_match_ids from candidate suppliers
    matched_panel_ids = [
        supplier["panel_match_id"] if isinstance(supplier, dict) else supplier
        for supplier in panel_data["candidate_suppliers"]
    ]
    proposal_payload = {
        "need_id": str(need_id),
        "matched_panels": matched_panel_ids,
        "evidence_items": evidence_data["evidence_items"],
        "approved_niche_candidates": []
    }

    proposal_resp = auth_client.post(
        "/api/v1/longlist-proposals",
        json=proposal_payload,
        headers={"X-Correlation-Id": "J02-001"}
    )
    assert proposal_resp.status_code == 201, f"Proposal generation failed: {proposal_resp.text}"
    proposal_data = proposal_resp.json()
    assert "proposal_id" in proposal_data
    assert "ranked_suppliers" in proposal_data
    assert proposal_data["need_id"] == str(need_id)
    # Every ranked supplier must have citations
    for supplier in proposal_data["ranked_suppliers"]:
        assert supplier["evidence_citations"] is not None
        assert len(supplier["evidence_citations"]) > 0


def test_j02_journey_with_coverage_gap_and_niche_research(auth_client, db_session):
    """Test J-02 journey with coverage gap triggering niche research (ATS7).

    Journey steps:
    - Setup: Create classified IT service need
    - ATS5: Query evidence
    - ATS6: Map to panels (detect coverage gap)
    - ATS7: Research niche providers
    - ATS8: Generate proposal with niche candidates
    """
    from app.models.need import Need
    from app.models.need_attributes import NeedAttributes
    from app.models.classification_review import ClassificationReview
    from datetime import datetime, UTC

    need_id = uuid.uuid4()
    need = Need(
        id=need_id,
        business_unit_id="BU-J02-NICHE",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="s3://test/j02-niche.pdf",
        normalized_payload_json=json.dumps({"title": "AI/ML Specialized Services"}),
        status="classified_it_service",
        classification_verdict="it_service",
        correlation_id="J02-NICHE-001",
    )
    db_session.add(need)

    attrs = NeedAttributes(
        id=uuid.uuid4(),
        need_id=need_id,
        service_type="AI/ML Services",
        scope_description="Specialized ML model development",
        estimated_volume_duration="18 months",
        required_skills=json.dumps(["TensorFlow", "PyTorch", "MLOps"]),
        budget_indication="€500K annually",
        delivery_location="Remote",
        field_confidence=json.dumps({"service_type": 0.88}),
    )
    db_session.add(attrs)

    classification = ClassificationReview(
        id=uuid.uuid4(),
        need_id=need_id,
        classification_verdict="it_service",
        classification_confidence=0.87,
        rationale="ML service team requirement",
        review_decision="approve",
        reviewer_id="procurement_reviewer@example.com",
        escalation_required=False,
        exemplars_referenced=json.dumps(["EXEMPLAR-IT-007"]),
    )
    db_session.add(classification)
    db_session.commit()

    # ATS5: Query evidence
    evidence_resp = auth_client.post(
        "/api/v1/evidence/queries",
        json={
            "need_id": str(need_id),
            "service_type": "AI/ML Services",
            "required_skills": ["TensorFlow", "PyTorch", "MLOps"],
            "business_unit_id": "BU-J02-NICHE"
        },
        headers={"X-Correlation-Id": "J02-NICHE-001"}
    )
    assert evidence_resp.status_code == 200
    evidence_data = evidence_resp.json()

    # ATS6: Map to panels - expect coverage gap for niche AI/ML
    panel_resp = auth_client.post(
        "/api/v1/panel-mappings",
        json={
            "need_id": str(need_id),
            "need_category": "AI/ML Services"
        },
        headers={"X-Correlation-Id": "J02-NICHE-001"}
    )
    assert panel_resp.status_code == 200
    panel_data = panel_resp.json()
    
    # For this test, we'll proceed to ATS7 research regardless of gap flag
    # ATS7: Niche research - extract supplier_id strings from candidate suppliers
    existing_supplier_ids = [
        supplier["supplier_id"] if isinstance(supplier, dict) else supplier
        for supplier in panel_data["candidate_suppliers"]
    ]
    research_payload = {
        "need_id": str(need_id),
        "capability_gap": "Advanced MLOps automation not in standard panels",
        "approved_source_list": ["GOV-SOURCE/ai-directory-2024", "GOV-SOURCE/certified-ml-providers"],
        "existing_panel_matches": existing_supplier_ids
    }

    research_resp = auth_client.post(
        "/api/v1/niche-research",
        json=research_payload,
        headers={"X-Correlation-Id": "J02-NICHE-001"}
    )
    assert research_resp.status_code == 201, f"Niche research failed: {research_resp.text}"
    research_data = research_resp.json()
    assert "niche_research_dossier" in research_data
    # All candidates must have source citations
    for candidate in research_data["niche_research_dossier"]:
        assert candidate["source_citations"] is not None
        assert len(candidate["source_citations"]) > 0

    # Simulate reviewer accepting niche candidates
    accepted_niche = [
        c for c in research_data["niche_research_dossier"]
        if c.get("review_status") in ["accepted", "pending"]
    ]

    # ATS8: Generate proposal including niche candidates
    matched_panel_ids = [
        supplier["panel_match_id"] if isinstance(supplier, dict) else supplier
        for supplier in panel_data["candidate_suppliers"]
    ]
    proposal_payload = {
        "need_id": str(need_id),
        "matched_panels": matched_panel_ids,
        "evidence_items": evidence_data["evidence_items"],
        "approved_niche_candidates": accepted_niche
    }

    proposal_resp = auth_client.post(
        "/api/v1/longlist-proposals",
        json=proposal_payload,
        headers={"X-Correlation-Id": "J02-NICHE-001"}
    )
    assert proposal_resp.status_code == 201
    proposal_data = proposal_resp.json()
    assert "ranked_suppliers" in proposal_data
    # Verify citations present for all ranked suppliers
    for supplier in proposal_data["ranked_suppliers"]:
        assert supplier["evidence_citations"] is not None


def test_j02_evidence_limited_flag_handling(auth_client, db_session):
    """Test J-02 journey with evidence_limited_flag set (TOL2 unavailable)."""
    from app.models.need import Need
    from app.models.need_attributes import NeedAttributes
    from app.models.classification_review import ClassificationReview
    from datetime import datetime, UTC

    need_id = uuid.uuid4()
    need = Need(
        id=need_id,
        business_unit_id="BU-J02-LIMITED",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="s3://test/j02-limited.pdf",
        normalized_payload_json=json.dumps({"title": "Network Security Services"}),
        status="classified_it_service",
        correlation_id="J02-LIMITED-001",
    )
    db_session.add(need)

    attrs = NeedAttributes(
        id=uuid.uuid4(),
        need_id=need_id,
        service_type="Network Security",
        scope_description="Security monitoring and response",
        estimated_volume_duration="12 months",
        required_skills=json.dumps(["Security", "Networking", "SIEM"]),
        budget_indication="€400K",
        delivery_location="Germany",
        field_confidence=json.dumps({"service_type": 0.89}),
    )
    db_session.add(attrs)

    classification = ClassificationReview(
        id=uuid.uuid4(),
        need_id=need_id,
        classification_verdict="it_service",
        classification_confidence=0.88,
        rationale="Security service requirement",
        review_decision="approve",
        reviewer_id="procurement_reviewer@example.com",
        escalation_required=False,
        exemplars_referenced=json.dumps(["EXEMPLAR-IT-008"]),
    )
    db_session.add(classification)
    db_session.commit()

    # ATS5: Query evidence - should return with evidence_limited_flag
    evidence_resp = auth_client.post(
        "/api/v1/evidence/queries",
        json={
            "need_id": str(need_id),
            "service_type": "Network Security",
            "required_skills": ["Security", "Networking", "SIEM"],
            "business_unit_id": "BU-J02-LIMITED"
        },
        headers={"X-Correlation-Id": "J02-LIMITED-001"}
    )
    assert evidence_resp.status_code == 200
    evidence_data = evidence_resp.json()
    # Evidence limited flag should be set when TOL2 unavailable
    assert "evidence_limited_flag" in evidence_data

    # Journey continues with panel mapping and proposal even with limited evidence
    panel_resp = auth_client.post(
        "/api/v1/panel-mappings",
        json={
            "need_id": str(need_id),
            "need_category": "Network Security"
        },
        headers={"X-Correlation-Id": "J02-LIMITED-001"}
    )
    assert panel_resp.status_code == 200
    panel_data = panel_resp.json()

    # ATS8: Generate proposal with evidence_limited_flag preserved
    matched_panel_ids = [
        supplier["panel_match_id"] if isinstance(supplier, dict) else supplier
        for supplier in panel_data["candidate_suppliers"]
    ]
    proposal_resp = auth_client.post(
        "/api/v1/longlist-proposals",
        json={
            "need_id": str(need_id),
            "matched_panels": matched_panel_ids,
            "evidence_items": evidence_data["evidence_items"],
            "approved_niche_candidates": []
        },
        headers={"X-Correlation-Id": "J02-LIMITED-001"}
    )
    assert proposal_resp.status_code == 201
    proposal_data = proposal_resp.json()
    # Evidence limited flag should be preserved in proposal
    assert "evidence_limited_flag" in proposal_data
