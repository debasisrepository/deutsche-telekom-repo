"""Unit tests for AGN3 service."""
import json

import pytest
from sqlalchemy.orm import Session

from app.models.longlist_proposal import LonglistProposal
from app.models.need_case import NeedCase
from app.models.normalized_need import NormalizedNeed
from app.models.proposal_supplier import ProposalSupplier
from app.models.supplier import Supplier
from app.services.agents.agn3_service import AGN3Service


@pytest.fixture
def test_case_setup(db_session: Session):
    """Create a test case with proposal and suppliers."""
    case = NeedCase(
        case_number="CASE-AGN3-001",
        inbound_channel="email",
        workflow_state="longlist_pending",
        next_action="Review longlist",
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
    
    # Create suppliers
    supplier1 = Supplier(supplier_code="SUP-AGN3-001", display_name="AGN3 Supplier 1", status="active")
    supplier2 = Supplier(supplier_code="SUP-AGN3-002", display_name="AGN3 Supplier 2", status="active")
    supplier3 = Supplier(supplier_code="SUP-AGN3-003", display_name="AGN3 Supplier 3", status="active")
    supplier4 = Supplier(supplier_code="SUP-AGN3-004", display_name="AGN3 Supplier 4", status="active")
    db_session.add_all([supplier1, supplier2, supplier3, supplier4])
    db_session.flush()
    
    # Create proposal with 3 suppliers
    proposal = LonglistProposal(case_id=case.id, version_no=1, proposal_status="draft")
    db_session.add(proposal)
    db_session.flush()
    
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
        "suppliers": [supplier1, supplier2, supplier3, supplier4]
    }


def test_capture_adjustment_add_new_supplier(db_session: Session, test_case_setup):
    """Test capturing an 'add' adjustment for a new supplier."""
    case = test_case_setup["case"]
    new_supplier = test_case_setup["suppliers"][3]  # Supplier not in proposal
    
    agn3_service = AGN3Service(db_session)
    
    result = agn3_service.capture_adjustment(
        case_id=case.id,
        supplier_id=new_supplier.id,
        change_type="add",
        rationale="Business unit requested additional supplier",
        actor_id="user_123"
    )
    
    assert result["case_id"] == case.id
    assert result["supplier_id"] == new_supplier.id
    assert result["change_type"] == "add"
    assert result["resulting_supplier_count"] == 4  # Was 3, now 4
    assert result["actor_id"] == "user_123"
    assert "adjustment_id" in result


def test_capture_adjustment_remove_existing_supplier(db_session: Session, test_case_setup):
    """Test capturing a 'remove' adjustment for an existing supplier."""
    case = test_case_setup["case"]
    existing_supplier = test_case_setup["suppliers"][0]  # Supplier in proposal
    
    agn3_service = AGN3Service(db_session)
    
    result = agn3_service.capture_adjustment(
        case_id=case.id,
        supplier_id=existing_supplier.id,
        change_type="remove",
        rationale="Failed compliance check",
        actor_id="user_123"
    )
    
    assert result["case_id"] == case.id
    assert result["supplier_id"] == existing_supplier.id
    assert result["change_type"] == "remove"
    assert result["resulting_supplier_count"] == 2  # Was 3, now 2
    assert result["rationale"] == "Failed compliance check"


def test_capture_adjustment_add_duplicate_supplier(db_session: Session, test_case_setup):
    """Test adding a supplier that's already in the proposal."""
    case = test_case_setup["case"]
    existing_supplier = test_case_setup["suppliers"][0]  # Already in proposal
    
    agn3_service = AGN3Service(db_session)
    
    result = agn3_service.capture_adjustment(
        case_id=case.id,
        supplier_id=existing_supplier.id,
        change_type="add",
        rationale="Attempted duplicate add",
        actor_id="user_123"
    )
    
    # Count should remain the same since supplier is already present
    assert result["resulting_supplier_count"] == 3


def test_capture_adjustment_remove_non_existent_supplier(db_session: Session, test_case_setup):
    """Test removing a supplier that's not in the proposal."""
    case = test_case_setup["case"]
    non_existent_supplier = test_case_setup["suppliers"][3]  # Not in proposal
    
    agn3_service = AGN3Service(db_session)
    
    result = agn3_service.capture_adjustment(
        case_id=case.id,
        supplier_id=non_existent_supplier.id,
        change_type="remove",
        rationale="Attempted removal of non-existent",
        actor_id="user_123"
    )
    
    # Count should remain the same since supplier wasn't present
    assert result["resulting_supplier_count"] == 3


def test_capture_adjustment_invalid_change_type(db_session: Session, test_case_setup):
    """Test that invalid change_type raises ValueError."""
    case = test_case_setup["case"]
    supplier = test_case_setup["suppliers"][0]
    
    agn3_service = AGN3Service(db_session)
    
    with pytest.raises(ValueError, match="Invalid change_type"):
        agn3_service.capture_adjustment(
            case_id=case.id,
            supplier_id=supplier.id,
            change_type="invalid",
            rationale="Test",
            actor_id="user_123"
        )


def test_capture_adjustment_no_proposal(db_session: Session):
    """Test that adjustment without proposal raises ValueError."""
    # Create case without proposal
    case = NeedCase(
        case_number="CASE-NO-PROPOSAL",
        inbound_channel="email",
        workflow_state="intake_pending",
        next_action="Extract attributes",
        created_by=1
    )
    db_session.add(case)
    db_session.commit()
    
    agn3_service = AGN3Service(db_session)
    
    with pytest.raises(ValueError, match="No longlist proposal found"):
        agn3_service.capture_adjustment(
            case_id=case.id,
            supplier_id=1,
            change_type="add",
            rationale="Test",
            actor_id="user_123"
        )
