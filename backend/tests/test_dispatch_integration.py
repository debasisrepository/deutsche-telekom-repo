"""Integration tests for tender dispatch functionality."""
import pytest
from sqlalchemy.orm import Session

from app.models.locked_longlist import LockedLonglist
from app.models.locked_supplier import LockedSupplier
from app.models.tender_dispatch import TenderDispatch
from app.repositories.dispatch_repository import DispatchRepository
from app.services.agents.agn3_service import AGN3Service
from app.services.policy.longlist_policy_service import LonglistPolicyService


def test_dispatch_creates_recipients(db_session: Session, seeded_locked_case):
    """Test that dispatch creates per-supplier recipient records."""
    case = seeded_locked_case
    
    # Dispatch tender
    agn3_service = AGN3Service(db_session)
    dispatch_result = agn3_service.dispatch_tender(
        case_id=case.id,
        actor_id="user-123"
    )
    db_session.commit()
    
    # Verify dispatch record created
    assert dispatch_result["dispatch_id"] is not None
    assert dispatch_result["dispatch_batch_ref"] is not None
    assert dispatch_result["dispatch_status"] in ("success", "partial_failure", "failed")
    assert dispatch_result["total_recipients"] > 0
    
    # Verify recipients created
    dispatch_repo = DispatchRepository(db_session)
    recipients = dispatch_repo.list_dispatch_recipients(dispatch_result["dispatch_id"])
    assert len(recipients) == dispatch_result["total_recipients"]
    
    # Verify each recipient has delivery status
    for recipient in recipients:
        assert recipient.delivery_status in ("success", "failed")


def test_dispatch_precondition_requires_lock(db_session: Session, seeded_case_without_lock):
    """Test that dispatch requires locked longlist."""
    case = seeded_case_without_lock
    
    # Assert dispatch preconditions should fail
    policy_service = LonglistPolicyService(db_session)
    with pytest.raises(ValueError, match="must be locked before dispatch"):
        policy_service.assert_dispatch_preconditions(case.id)


def test_dispatch_prevents_duplicate_dispatch(db_session: Session, seeded_locked_case):
    """Test that dispatching already-dispatched case fails."""
    case = seeded_locked_case
    
    # First dispatch succeeds
    agn3_service = AGN3Service(db_session)
    agn3_service.dispatch_tender(case_id=case.id, actor_id="user-123")
    db_session.commit()
    
    # Second dispatch should fail
    with pytest.raises(ValueError, match="already been dispatched"):
        agn3_service.dispatch_tender(case_id=case.id, actor_id="user-456")


def test_dispatch_endpoint_returns_recipients(client, auth_client, db_session, seeded_locked_case):
    """Test POST /api/v1/cases/{caseId}/dispatch endpoint."""
    case = seeded_locked_case
    
    # Dispatch via endpoint
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/dispatch",
        json={"actor_id": "user-123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["dispatch_id"] is not None
    assert data["dispatch_batch_ref"] is not None
    assert data["dispatch_status"] in ("success", "partial_failure", "failed")
    assert "recipients" in data
    assert len(data["recipients"]) > 0
    
    # Verify recipient structure
    for recipient in data["recipients"]:
        assert "supplier_id" in recipient
        assert "delivery_status" in recipient
        assert recipient["delivery_status"] in ("success", "failed")


def test_dispatch_endpoint_blocks_without_lock(client, auth_client, db_session, seeded_case_without_lock):
    """Test dispatch endpoint blocks when case not locked."""
    case = seeded_case_without_lock
    
    # Attempt dispatch without lock
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/dispatch",
        json={"actor_id": "user-123"}
    )
    
    assert response.status_code == 409
    assert "must be locked" in response.json()["detail"]


def test_dispatch_records_batch_reference(db_session: Session, seeded_locked_case):
    """Test that dispatch generates unique batch reference."""
    case = seeded_locked_case
    
    # Dispatch tender
    agn3_service = AGN3Service(db_session)
    dispatch_result = agn3_service.dispatch_tender(case_id=case.id, actor_id="user-123")
    db_session.commit()
    
    # Verify batch reference format
    batch_ref = dispatch_result["dispatch_batch_ref"]
    assert batch_ref.startswith(f"BATCH-{case.id}-")
    
    # Verify batch reference stored in database
    dispatch = db_session.query(TenderDispatch).filter_by(id=dispatch_result["dispatch_id"]).first()
    assert dispatch.dispatch_batch_ref == batch_ref


def test_dispatch_status_reflects_outcomes(db_session: Session, seeded_locked_case):
    """Test that dispatch status correctly reflects recipient outcomes."""
    case = seeded_locked_case
    
    # Dispatch tender
    agn3_service = AGN3Service(db_session)
    dispatch_result = agn3_service.dispatch_tender(case_id=case.id, actor_id="user-123")
    db_session.commit()
    
    # Count success and failure outcomes
    recipients = dispatch_result["recipients"]
    success_count = sum(1 for r in recipients if r["delivery_status"] == "success")
    failed_count = sum(1 for r in recipients if r["delivery_status"] == "failed")
    
    # Verify dispatch status logic
    if failed_count == 0:
        assert dispatch_result["dispatch_status"] == "success"
    elif success_count == 0:
        assert dispatch_result["dispatch_status"] == "failed"
    else:
        assert dispatch_result["dispatch_status"] == "partial_failure"


@pytest.fixture
def seeded_locked_case(db_session: Session):
    """Create seeded case with locked longlist for testing."""
    from app.models.longlist_proposal import LonglistProposal
    from app.models.need_case import NeedCase
    from app.models.normalized_need import NormalizedNeed
    from app.models.proposal_supplier import ProposalSupplier
    from app.models.supplier import Supplier
    
    # Create case
    case = NeedCase(
        case_number="CASE-TEST-DISPATCH-001",
        inbound_channel="email",
        workflow_state="dispatch_pending",
        next_action="dispatch_tender",
        created_by="1",
        requirement_tags="REQ-DOMAIN-001"
    )
    db_session.add(case)
    db_session.flush()
    
    # Create normalized need
    need = NormalizedNeed(
        case_id=case.id,
        mandatory_fields='{"service_category": "cloud"}',
        sourced_fields='{}',
        derived_fields='{}',
        completeness_score=1.0,
        requirement_tags="REQ-DATA-002"
    )
    db_session.add(need)
    
    # Create suppliers
    suppliers = []
    for i in range(4):
        supplier = Supplier(
            supplier_code=f"SUP-DISPATCH-{i+1:03d}",
            display_name=f"Test Supplier {i+1}",
            status="active",
            requirement_tags="REQ-INT-002"
        )
        db_session.add(supplier)
        db_session.flush()
        suppliers.append(supplier)
    
    # Create proposal
    proposal = LonglistProposal(
        case_id=case.id,
        version_no=1,
        proposal_status="finalized",
        requirement_tags="REQ-DOMAIN-006"
    )
    db_session.add(proposal)
    db_session.flush()
    
    # Create proposal suppliers
    for i, supplier in enumerate(suppliers):
        ps = ProposalSupplier(
            proposal_id=proposal.id,
            supplier_id=supplier.id,
            rank_position=i + 1,
            recommendation_status="recommended",
            ranking_score=100.0 - (i * 10),
            citation_complete=True,
            requirement_tags="REQ-DOMAIN-007"
        )
        db_session.add(ps)
    
    # Create locked longlist
    locked_longlist = LockedLonglist(
        case_id=case.id,
        source_proposal_id=proposal.id,
        lock_status="locked",
        locked_by="system",
        requirement_tags="REQ-DOMAIN-010"
    )
    db_session.add(locked_longlist)
    db_session.flush()
    
    # Create locked suppliers
    for i, supplier in enumerate(suppliers):
        locked_supplier = LockedSupplier(
            locked_longlist_id=locked_longlist.id,
            supplier_id=supplier.id,
            final_rank_position=i + 1,
            requirement_tags="REQ-DOMAIN-010"
        )
        db_session.add(locked_supplier)
    
    db_session.commit()
    return case


@pytest.fixture
def seeded_case_without_lock(db_session: Session):
    """Create seeded case without locked longlist for testing."""
    from app.models.need_case import NeedCase
    from app.models.normalized_need import NormalizedNeed
    
    # Create case
    case = NeedCase(
        case_number="CASE-TEST-NOLOCK-001",
        inbound_channel="email",
        workflow_state="longlist_pending",
        next_action="lock_longlist",
        created_by="1",
        requirement_tags="REQ-DOMAIN-001"
    )
    db_session.add(case)
    db_session.flush()
    
    # Create normalized need
    need = NormalizedNeed(
        case_id=case.id,
        mandatory_fields='{"service_category": "cloud"}',
        sourced_fields='{}',
        derived_fields='{}',
        completeness_score=1.0,
        requirement_tags="REQ-DATA-002"
    )
    db_session.add(need)
    db_session.commit()
    return case
