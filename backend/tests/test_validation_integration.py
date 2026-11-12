"""Integration tests for supplier-count validation endpoints."""
import json

import pytest
from sqlalchemy.orm import Session

from app.models.longlist_proposal import LonglistProposal
from app.models.need_case import NeedCase
from app.models.normalized_need import NormalizedNeed
from app.models.proposal_supplier import ProposalSupplier
from app.models.supplier import Supplier


@pytest.fixture
def case_with_valid_count(db_session: Session):
    """Create a case with valid supplier count (3-6)."""
    case = NeedCase(
        case_number="CASE-VALID-001",
        inbound_channel="email",
        workflow_state="longlist_pending",
        next_action="Validate longlist",
        created_by=1
    )
    db_session.add(case)
    
    normalized = NormalizedNeed(
        case=case,
        mandatory_fields=json.dumps({"service_category": "cloud"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=0.9
    )
    db_session.add(normalized)
    
    # Create 4 suppliers (within 3-6 range)
    suppliers = []
    for i in range(4):
        s = Supplier(
            supplier_code=f"SUP-VALID-{i+1:03d}",
            display_name=f"Valid Supplier {i+1}",
            status="active"
        )
        suppliers.append(s)
        db_session.add(s)
    
    db_session.flush()
    
    proposal = LonglistProposal(
        case_id=case.id,
        version_no=1,
        proposal_status="draft"
    )
    db_session.add(proposal)
    db_session.flush()
    
    for i, supplier in enumerate(suppliers):
        ps = ProposalSupplier(
            proposal_id=proposal.id,
            supplier_id=supplier.id,
            rank_position=i+1,
            recommendation_status="recommended",
            ranking_score=0.9 - (i * 0.1),
            citation_complete=True
        )
        db_session.add(ps)
    
    db_session.commit()
    
    return {"case": case, "proposal": proposal, "suppliers": suppliers}


@pytest.fixture
def case_with_low_count(db_session: Session):
    """Create a case with too few suppliers (< 3)."""
    case = NeedCase(
        case_number="CASE-LOW-001",
        inbound_channel="email",
        workflow_state="longlist_pending",
        next_action="Validate longlist",
        created_by=1
    )
    db_session.add(case)
    
    normalized = NormalizedNeed(
        case=case,
        mandatory_fields=json.dumps({"service_category": "cloud"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=0.9
    )
    db_session.add(normalized)
    
    # Create only 2 suppliers (below minimum)
    suppliers = []
    for i in range(2):
        s = Supplier(
            supplier_code=f"SUP-LOW-{i+1:03d}",
            display_name=f"Low Supplier {i+1}",
            status="active"
        )
        suppliers.append(s)
        db_session.add(s)
    
    db_session.flush()
    
    proposal = LonglistProposal(
        case_id=case.id,
        version_no=1,
        proposal_status="draft"
    )
    db_session.add(proposal)
    db_session.flush()
    
    for i, supplier in enumerate(suppliers):
        ps = ProposalSupplier(
            proposal_id=proposal.id,
            supplier_id=supplier.id,
            rank_position=i+1,
            recommendation_status="recommended",
            ranking_score=0.9 - (i * 0.1),
            citation_complete=True
        )
        db_session.add(ps)
    
    db_session.commit()
    
    return {"case": case, "proposal": proposal, "suppliers": suppliers}


@pytest.fixture
def case_with_high_count(db_session: Session):
    """Create a case with too many suppliers (> 6)."""
    case = NeedCase(
        case_number="CASE-HIGH-001",
        inbound_channel="email",
        workflow_state="longlist_pending",
        next_action="Validate longlist",
        created_by=1
    )
    db_session.add(case)
    
    normalized = NormalizedNeed(
        case=case,
        mandatory_fields=json.dumps({"service_category": "cloud"}),
        sourced_fields=json.dumps({}),
        derived_fields=json.dumps({}),
        completeness_score=0.9
    )
    db_session.add(normalized)
    
    # Create 8 suppliers (above maximum)
    suppliers = []
    for i in range(8):
        s = Supplier(
            supplier_code=f"SUP-HIGH-{i+1:03d}",
            display_name=f"High Supplier {i+1}",
            status="active"
        )
        suppliers.append(s)
        db_session.add(s)
    
    db_session.flush()
    
    proposal = LonglistProposal(
        case_id=case.id,
        version_no=1,
        proposal_status="draft"
    )
    db_session.add(proposal)
    db_session.flush()
    
    for i, supplier in enumerate(suppliers):
        ps = ProposalSupplier(
            proposal_id=proposal.id,
            supplier_id=supplier.id,
            rank_position=i+1,
            recommendation_status="recommended",
            ranking_score=0.9 - (i * 0.05),
            citation_complete=True
        )
        db_session.add(ps)
    
    db_session.commit()
    
    return {"case": case, "proposal": proposal, "suppliers": suppliers}


def test_validation_valid_supplier_count(auth_client, case_with_valid_count):
    """Test validation with valid supplier count (3-6)."""
    case = case_with_valid_count["case"]
    
    response = auth_client.post(f"/api/v1/cases/{case.id}/validations/supplier-count")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["case_id"] == case.id
    assert data["validation_type"] == "supplier_count"
    assert data["supplier_count"] == 4
    assert data["validation_result"] == "valid"
    assert "validation_id" in data
    assert "rule_snapshot" in data
    assert "validated_at" in data


def test_validation_invalid_low_supplier_count(auth_client, case_with_low_count):
    """Test validation blocks finalization with too few suppliers."""
    case = case_with_low_count["case"]
    
    response = auth_client.post(f"/api/v1/cases/{case.id}/validations/supplier-count")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["case_id"] == case.id
    assert data["supplier_count"] == 2
    assert data["validation_result"] == "invalid_low"
    assert "below minimum" in data["validation_message"]


def test_validation_invalid_high_supplier_count(auth_client, case_with_high_count):
    """Test validation flags longlists with too many suppliers."""
    case = case_with_high_count["case"]
    
    response = auth_client.post(f"/api/v1/cases/{case.id}/validations/supplier-count")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["case_id"] == case.id
    assert data["supplier_count"] == 8
    assert data["validation_result"] == "invalid_high"
    assert "above maximum" in data["validation_message"]


def test_validation_outcome_stored(auth_client, case_with_valid_count, db_session: Session):
    """Test that validation outcome is stored in database."""
    case = case_with_valid_count["case"]
    
    response = auth_client.post(f"/api/v1/cases/{case.id}/validations/supplier-count")
    assert response.status_code == 200
    
    # Query from database
    from app.models.policy_validation import PolicyValidation
    
    validation = db_session.query(PolicyValidation).filter(
        PolicyValidation.case_id == case.id,
        PolicyValidation.validation_type == "supplier_count"
    ).first()
    
    assert validation is not None
    assert validation.supplier_count == 4
    assert validation.validation_result == "valid"
    assert validation.rule_snapshot is not None


def test_validation_rule_snapshot_captured(auth_client, case_with_valid_count):
    """Test that rule snapshot is captured for audit compliance."""
    case = case_with_valid_count["case"]
    
    response = auth_client.post(f"/api/v1/cases/{case.id}/validations/supplier-count")
    
    assert response.status_code == 200
    data = response.json()
    
    # Rule snapshot should be present
    assert "rule_snapshot" in data
    rule_snapshot = json.loads(data["rule_snapshot"])
    assert "rule_type" in rule_snapshot
    assert "min_suppliers" in rule_snapshot
    assert "max_suppliers" in rule_snapshot
    assert rule_snapshot["min_suppliers"] == 3
    assert rule_snapshot["max_suppliers"] == 6


def test_validation_case_not_found(auth_client):
    """Test validation on non-existent case returns 404."""
    response = auth_client.post("/api/v1/cases/99999/validations/supplier-count")
    
    assert response.status_code == 404
