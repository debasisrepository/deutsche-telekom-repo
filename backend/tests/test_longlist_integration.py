"""Integration tests for longlist proposal functionality."""
import json


def test_create_longlist_proposal_endpoint(auth_client, db_session):
    """Test POST /api/v1/cases/{caseId}/longlist-proposals endpoint."""
    from app.models.case_evidence import CaseEvidence
    from app.models.need_case import NeedCase
    from app.models.normalized_need import NormalizedNeed
    from app.models.supplier import Supplier
    
    # Create test case
    case = NeedCase(
        case_number="LONG-TEST-001",
        inbound_channel="rfp_document",
        workflow_state="extraction_approved",
        next_action="generate_longlist",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    # Add normalized need
    normalized = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({"service_category": "software_development"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=1.0
    )
    db_session.add(normalized)
    
    # Add supplier and evidence
    supplier = Supplier(
        supplier_code="TEST-SUP-001",
        display_name="Test Supplier",
        status="active"
    )
    db_session.add(supplier)
    db_session.flush()
    
    evidence = CaseEvidence(
        case_id=case.id,
        supplier_id=supplier.id,
        citation_label="Test Evidence",
        citation_ref="test/ref",
        evidence_summary="Test summary",
        evidence_found=True
    )
    db_session.add(evidence)
    db_session.commit()
    
    # Call endpoint
    response = auth_client.post(f"/api/v1/cases/{case.id}/longlist-proposals")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == len(data["items"])
    assert "proposal_id" in data
    assert data["proposal_status"] == "draft"


def test_longlist_proposal_response_shape(auth_client, db_session):
    """Test that longlist proposal returns {items, total} wrapper with ranked suppliers."""
    from app.models.case_evidence import CaseEvidence
    from app.models.need_case import NeedCase
    from app.models.normalized_need import NormalizedNeed
    from app.models.supplier import Supplier
    
    # Create test case with multiple suppliers
    case = NeedCase(
        case_number="LONG-TEST-002",
        inbound_channel="email",
        workflow_state="extraction_approved",
        next_action="generate_longlist",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    normalized = NormalizedNeed(
        case_id=case.id,
        mandatory_fields=json.dumps({"service_category": "cloud"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=1.0
    )
    db_session.add(normalized)
    
    # Add multiple suppliers with evidence
    for i in range(3):
        supplier = Supplier(
            supplier_code=f"TEST-SUP-{i+100}",
            display_name=f"Test Supplier {i+1}",
            status="active"
        )
        db_session.add(supplier)
        db_session.flush()
        
        evidence = CaseEvidence(
            case_id=case.id,
            supplier_id=supplier.id,
            citation_label=f"Evidence {i+1}",
            citation_ref=f"test/ref/{i+1}",
            evidence_summary=f"Summary {i+1}",
            evidence_found=True
        )
        db_session.add(evidence)
    
    db_session.commit()
    
    # Call endpoint
    response = auth_client.post(f"/api/v1/cases/{case.id}/longlist-proposals")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 3
    
    # Verify supplier structure includes ranking fields
    for idx, supplier in enumerate(data["items"]):
        assert "rank_position" in supplier
        assert supplier["rank_position"] == idx + 1
        assert "ranking_score" in supplier
        assert "citation_complete" in supplier
        assert isinstance(supplier["citation_complete"], bool)


def test_longlist_repository(db_session):
    """Test longlist repository CRUD operations."""
    from app.models.need_case import NeedCase
    from app.models.supplier import Supplier
    from app.repositories.longlist_repository import LonglistRepository
    
    repo = LonglistRepository(db_session)
    
    # Create test case and supplier
    case = NeedCase(
        case_number="REPO-TEST-001",
        inbound_channel="rfp_document",
        workflow_state="extraction_approved",
        next_action="generate_longlist",
        created_by=1
    )
    db_session.add(case)
    db_session.flush()
    
    supplier = Supplier(
        supplier_code="REPO-SUP-001",
        display_name="Repository Test Supplier",
        status="active"
    )
    db_session.add(supplier)
    db_session.flush()
    
    # Create proposal
    proposal = repo.create_proposal(
        case_id=case.id,
        version_no=1,
        proposal_status="draft",
        generation_inputs=json.dumps({"test": "data"}),
        generated_by_agent_run_id="test-run-1"
    )
    
    assert proposal.id is not None
    assert proposal.case_id == case.id
    
    # Create proposal supplier
    ps = repo.create_proposal_supplier(
        proposal_id=proposal.id,
        supplier_id=supplier.id,
        rank_position=1,
        recommendation_status="recommended",
        ranking_score=0.95,
        citation_complete=True
    )
    
    assert ps.id is not None
    assert ps.rank_position == 1
    
    # List proposals
    proposals = repo.list_case_proposals(case.id)
    assert len(proposals) == 1
    assert proposals[0].id == proposal.id
    
    # Get proposal suppliers
    suppliers = repo.get_proposal_suppliers(proposal.id)
    assert len(suppliers) == 1
    assert suppliers[0].rank_position == 1
