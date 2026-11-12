"""Integration tests for evidence retrieval and citation."""
import json

from app.models.case_evidence import CaseEvidence
from app.models.commissioned_sow import CommissionedSoW
from app.models.historical_order import HistoricalOrder
from app.models.need_case import NeedCase
from app.models.normalized_need import NormalizedNeed
from app.models.source_artifact import SourceArtifact
from app.models.supplier import Supplier
from app.services.evidence.evidence_service import EvidenceService


def test_evidence_service_store_evidence(db_session, test_user):
    """Test evidence service stores evidence with supplier and citation links."""
    # Create a case
    case = NeedCase(
        case_number="CASE-TEST-001",
        inbound_channel="rfp_document",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=test_user.id,
        requirement_tags="REQ-INT-002"
    )
    db_session.add(case)
    db_session.flush()
    
    normalized = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({
            "need_title": "Test Cloud Services",
            "business_unit": "IT",
            "need_description": "Cloud infrastructure needs"
        }),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=1.0
    )
    db_session.add(normalized)
    
    artifact = SourceArtifact(
        case_id=case.id,
        artifact_type="rfp_document",
        storage_ref="test-rfp.pdf",
        source_channel="rfp_document"
    )
    db_session.add(artifact)
    db_session.commit()
    
    # Store evidence using service
    evidence_service = EvidenceService(db_session)
    need_attributes = {"service_domain": "cloud_infrastructure"}
    evidence_records = evidence_service.store_evidence(
        case_id=case.id,
        need_attributes=need_attributes,
        requirement_tags="REQ-INT-002,REQ-DOMAIN-007"
    )
    
    # Verify evidence was created
    assert len(evidence_records) == 3
    assert all(isinstance(e, CaseEvidence) for e in evidence_records)
    assert all(e.evidence_found for e in evidence_records)
    
    # Verify suppliers were created
    suppliers = db_session.query(Supplier).all()
    assert len(suppliers) >= 3
    
    # Verify historical orders and SoWs were created
    orders = db_session.query(HistoricalOrder).all()
    sows = db_session.query(CommissionedSoW).all()
    assert len(orders) >= 2
    assert len(sows) >= 1


def test_evidence_service_list_evidence(db_session, test_user):
    """Test evidence service lists evidence with supplier details."""
    # Create case with evidence
    case = NeedCase(
        case_number="CASE-TEST-002",
        inbound_channel="email",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=test_user.id
    )
    db_session.add(case)
    db_session.flush()
    
    normalized = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({"need_title": "Test Need"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=1.0
    )
    db_session.add(normalized)
    db_session.commit()
    
    # Store evidence
    evidence_service = EvidenceService(db_session)
    evidence_service.store_evidence(
        case_id=case.id,
        need_attributes={"service_domain": "test"}
    )
    
    # List evidence
    evidence_list = evidence_service.list_evidence(case.id)
    
    assert len(evidence_list) == 3
    for item in evidence_list:
        assert "id" in item
        assert "case_id" in item
        assert item["case_id"] == case.id
        assert "supplier" in item
        assert item["supplier"] is not None
        assert "supplier_code" in item["supplier"]
        assert "display_name" in item["supplier"]
        assert "citation_label" in item
        assert "citation_ref" in item
        assert "evidence_summary" in item
        assert "evidence_found" in item
        assert item["evidence_found"] is True


def test_get_case_evidence_endpoint(auth_client, db_session, test_user):
    """Test GET /api/v1/cases/{caseId}/evidence endpoint."""
    # Create case with evidence
    case = NeedCase(
        case_number="CASE-TEST-003",
        inbound_channel="rfp_document",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=test_user.id
    )
    db_session.add(case)
    db_session.flush()
    
    normalized = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({"need_title": "API Test Case"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=1.0
    )
    db_session.add(normalized)
    db_session.commit()
    
    # Store evidence
    evidence_service = EvidenceService(db_session)
    evidence_service.store_evidence(case_id=case.id, need_attributes={})
    
    # Call endpoint
    response = auth_client.get(f"/api/v1/cases/{case.id}/evidence")
    
    assert response.status_code == 200
    data = response.json()
    assert "case_id" in data
    assert data["case_id"] == case.id
    assert "case_number" in data
    assert data["case_number"] == "CASE-TEST-003"
    assert "evidence_items" in data
    assert len(data["evidence_items"]) == 3
    assert "total" in data
    assert data["total"] == 3


def test_get_case_evidence_endpoint_not_found(auth_client):
    """Test evidence endpoint returns 404 for nonexistent case."""
    response = auth_client.get("/api/v1/cases/99999/evidence")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_evidence_repository_get_or_create_supplier(db_session):
    """Test evidence repository creates suppliers idempotently."""
    from app.repositories.evidence_repository import EvidenceRepository
    
    repo = EvidenceRepository(db_session)
    
    # Create supplier
    supplier1 = repo.get_or_create_supplier("TEST-SUP-001", "Test Supplier Inc")
    db_session.commit()
    
    assert supplier1.supplier_code == "TEST-SUP-001"
    assert supplier1.display_name == "Test Supplier Inc"
    assert supplier1.status == "active"
    
    # Get same supplier again (idempotent)
    supplier2 = repo.get_or_create_supplier("TEST-SUP-001", "Test Supplier Inc")
    db_session.commit()
    
    assert supplier1.id == supplier2.id


def test_evidence_found_flag(db_session, test_user):
    """Test evidence_found flag is stored correctly."""
    # Create case
    case = NeedCase(
        case_number="CASE-TEST-004",
        inbound_channel="email",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=test_user.id
    )
    db_session.add(case)
    db_session.flush()
    
    normalized = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({"need_title": "Test"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=1.0
    )
    db_session.add(normalized)
    db_session.commit()
    
    # Store evidence
    evidence_service = EvidenceService(db_session)
    evidence_records = evidence_service.store_evidence(case_id=case.id, need_attributes={})
    
    # Verify all records have evidence_found=True
    assert all(e.evidence_found for e in evidence_records)
    
    # List and verify
    evidence_list = evidence_service.list_evidence(case.id)
    assert all(item["evidence_found"] for item in evidence_list)


def test_agn5_retrieve_evidence_method(db_session):
    """Test AGN5 rule engine retrieve_evidence method."""
    from app.services.rules.agn5_rule_engine import AGN5RuleEngine
    
    engine = AGN5RuleEngine(db_session)
    
    # Call retrieve_evidence
    confirmed_attributes = {
        "service_category": {"value": "cloud_infrastructure"},
        "estimated_duration": {"value": "12_months"}
    }
    
    evidence = engine.retrieve_evidence(case_id=1, confirmed_attributes=confirmed_attributes)
    
    # Verify normalized evidence structure
    assert len(evidence) == 3
    for item in evidence:
        assert "supplier_code" in item
        assert "supplier_name" in item
        assert "evidence_type" in item
        assert "citation_label" in item
        assert "citation_ref" in item
        assert "evidence_summary" in item
        assert "evidence_found" in item


def test_evidence_linked_to_case(db_session, test_user):
    """Test evidence is properly linked to case."""
    # Create case
    case = NeedCase(
        case_number="CASE-TEST-005",
        inbound_channel="rfp_document",
        workflow_state="extraction_approved",
        next_action="classification_pending",
        created_by=test_user.id
    )
    db_session.add(case)
    db_session.flush()
    
    normalized = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({"need_title": "Link Test"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=1.0
    )
    db_session.add(normalized)
    db_session.commit()
    
    # Store evidence
    evidence_service = EvidenceService(db_session)
    evidence_service.store_evidence(case_id=case.id, need_attributes={})
    
    # Query evidence by case
    evidence_records = db_session.query(CaseEvidence).filter_by(case_id=case.id).all()
    
    assert len(evidence_records) == 3
    assert all(e.case_id == case.id for e in evidence_records)
