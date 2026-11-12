"""Integration tests for supplier adjustment endpoints."""
import json

import pytest
from sqlalchemy.orm import Session

from app.models.longlist_proposal import LonglistProposal
from app.models.need_case import NeedCase
from app.models.normalized_need import NormalizedNeed
from app.models.proposal_supplier import ProposalSupplier
from app.models.supplier import Supplier


@pytest.fixture
def test_case_with_proposal(db_session: Session):
    """Create a test case with a longlist proposal."""
    # Create case
    case = NeedCase(
        case_number="CASE-TEST-001",
        inbound_channel="email",
        workflow_state="longlist_pending",
        next_action="Review longlist",
        created_by=1
    )
    db_session.add(case)
    
    # Create normalized need
    normalized = NormalizedNeed(
        case=case,
        mandatory_fields=json.dumps({"service_category": "cloud", "business_unit": "IT"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=0.9
    )
    db_session.add(normalized)
    
    # Create suppliers
    supplier1 = Supplier(
        supplier_code="SUP-TEST-001",
        display_name="Test Supplier 1",
        status="active"
    )
    supplier2 = Supplier(
        supplier_code="SUP-TEST-002",
        display_name="Test Supplier 2",
        status="active"
    )
    supplier3 = Supplier(
        supplier_code="SUP-TEST-003",
        display_name="Test Supplier 3",
        status="active"
    )
    db_session.add_all([supplier1, supplier2, supplier3])
    db_session.flush()
    
    # Create longlist proposal
    proposal = LonglistProposal(
        case_id=case.id,
        version_no=1,
        proposal_status="draft"
    )
    db_session.add(proposal)
    db_session.flush()
    
    # Add proposal suppliers
    ps1 = ProposalSupplier(
        proposal_id=proposal.id,
        supplier_id=supplier1.id,
        rank_position=1,
        recommendation_status="recommended",
        ranking_score=0.95,
        citation_complete=True
    )
    ps2 = ProposalSupplier(
        proposal_id=proposal.id,
        supplier_id=supplier2.id,
        rank_position=2,
        recommendation_status="recommended",
        ranking_score=0.85,
        citation_complete=True
    )
    ps3 = ProposalSupplier(
        proposal_id=proposal.id,
        supplier_id=supplier3.id,
        rank_position=3,
        recommendation_status="recommended",
        ranking_score=0.75,
        citation_complete=True
    )
    db_session.add_all([ps1, ps2, ps3])
    db_session.commit()
    
    return {
        "case": case,
        "proposal": proposal,
        "suppliers": [supplier1, supplier2, supplier3]
    }


def test_capture_adjustment_add(auth_client, test_case_with_proposal, db_session: Session):
    """Test capturing an 'add' adjustment."""
    case = test_case_with_proposal["case"]
    
    # Create a new supplier to add
    new_supplier = Supplier(
        supplier_code="SUP-TEST-004",
        display_name="Test Supplier 4",
        status="active"
    )
    db_session.add(new_supplier)
    db_session.commit()
    
    # Call adjustment endpoint
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/adjustments",
        json={
            "supplier_id": new_supplier.id,
            "change_type": "add",
            "rationale": "Business unit requested additional supplier"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["case_id"] == case.id
    assert data["supplier_id"] == new_supplier.id
    assert data["change_type"] == "add"
    assert data["resulting_supplier_count"] == 4  # Was 3, now 4
    assert "adjustment_id" in data
    assert "created_at" in data


def test_capture_adjustment_remove(auth_client, test_case_with_proposal, db_session: Session):
    """Test capturing a 'remove' adjustment."""
    case = test_case_with_proposal["case"]
    suppliers = test_case_with_proposal["suppliers"]
    
    # Remove the first supplier
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/adjustments",
        json={
            "supplier_id": suppliers[0].id,
            "change_type": "remove",
            "rationale": "Supplier failed compliance check"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["case_id"] == case.id
    assert data["supplier_id"] == suppliers[0].id
    assert data["change_type"] == "remove"
    assert data["resulting_supplier_count"] == 2  # Was 3, now 2
    assert "adjustment_id" in data


def test_adjustment_history_remains_visible(auth_client, test_case_with_proposal, db_session: Session):
    """Test that adjustment history remains visible."""
    case = test_case_with_proposal["case"]
    suppliers = test_case_with_proposal["suppliers"]
    
    # Make several adjustments
    auth_client.post(
        f"/api/v1/cases/{case.id}/adjustments",
        json={
            "supplier_id": suppliers[0].id,
            "change_type": "remove",
            "rationale": "First removal"
        }
    )
    
    auth_client.post(
        f"/api/v1/cases/{case.id}/adjustments",
        json={
            "supplier_id": suppliers[0].id,
            "change_type": "add",
            "rationale": "Re-added after review"
        }
    )
    
    # Query adjustments from database
    from app.models.supplier_adjustment import SupplierAdjustment
    
    adjustments = db_session.query(SupplierAdjustment).filter(
        SupplierAdjustment.case_id == case.id
    ).order_by(SupplierAdjustment.created_at).all()
    
    assert len(adjustments) == 2
    assert adjustments[0].change_type == "remove"
    assert adjustments[1].change_type == "add"
    assert adjustments[0].rationale == "First removal"
    assert adjustments[1].rationale == "Re-added after review"


def test_adjustment_captures_actor_and_timestamp(auth_client, test_case_with_proposal, db_session: Session):
    """Test that adjustment captures actor ID and timestamp."""
    case = test_case_with_proposal["case"]
    suppliers = test_case_with_proposal["suppliers"]
    
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/adjustments",
        json={
            "supplier_id": suppliers[0].id,
            "change_type": "remove",
            "rationale": "Test adjustment"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Actor ID should be captured
    assert "actor_id" in data
    # Timestamp should be captured
    assert "created_at" in data


def test_adjustment_invalid_change_type(auth_client, test_case_with_proposal):
    """Test that invalid change_type is rejected."""
    case = test_case_with_proposal["case"]
    suppliers = test_case_with_proposal["suppliers"]
    
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/adjustments",
        json={
            "supplier_id": suppliers[0].id,
            "change_type": "invalid",
            "rationale": "Test"
        }
    )
    
    assert response.status_code == 400


def test_adjustment_case_not_found(auth_client, db_session: Session):
    """Test adjustment on non-existent case returns 404."""
    response = auth_client.post(
        "/api/v1/cases/99999/adjustments",
        json={
            "supplier_id": 1,
            "change_type": "add",
            "rationale": "Test"
        }
    )
    
    assert response.status_code == 404
