"""Integration tests for longlist lock functionality."""
import pytest
from sqlalchemy.orm import Session

from app.models.locked_supplier import LockedSupplier
from app.models.policy_validation import PolicyValidation
from app.repositories.lock_repository import LockRepository
from app.services.agents.agn3_service import AGN3Service
from app.services.policy.longlist_policy_service import LonglistPolicyService


def test_lock_longlist_creates_snapshot(db_session: Session, seeded_case_with_proposal):
    """Test that lock creates immutable supplier snapshot."""
    case = seeded_case_with_proposal
    
    # Create valid supplier-count validation
    validation = PolicyValidation(
        case_id=case.id,
        validation_type="supplier_count",
        supplier_count=4,
        validation_result="valid",
        rule_snapshot='{"min": 3, "max": 6}',
        requirement_tags="REQ-DOMAIN-009"
    )
    db_session.add(validation)
    db_session.commit()
    
    # Lock longlist
    agn3_service = AGN3Service(db_session)
    lock_result = agn3_service.lock_longlist(
        case_id=case.id,
        actor_id="user-123"
    )
    db_session.commit()
    
    # Verify locked longlist created
    assert lock_result["locked_longlist_id"] is not None
    assert lock_result["lock_status"] == "locked"
    assert lock_result["locked_by"] == "user-123"
    assert lock_result["total_suppliers"] > 0
    
    # Verify locked suppliers created
    lock_repo = LockRepository(db_session)
    locked_suppliers = lock_repo.list_locked_suppliers(lock_result["locked_longlist_id"])
    assert len(locked_suppliers) == lock_result["total_suppliers"]


def test_lock_precondition_requires_valid_validation(db_session: Session, seeded_case_with_proposal):
    """Test that lock requires valid supplier-count validation."""
    case = seeded_case_with_proposal
    
    # Create invalid_low supplier-count validation
    validation = PolicyValidation(
        case_id=case.id,
        validation_type="supplier_count",
        supplier_count=2,
        validation_result="invalid_low",
        rule_snapshot='{"min": 3, "max": 6}',
        requirement_tags="REQ-DOMAIN-009"
    )
    db_session.add(validation)
    db_session.commit()
    
    # Assert lock preconditions should fail
    policy_service = LonglistPolicyService(db_session)
    with pytest.raises(ValueError, match="validation result is 'invalid_low'"):
        policy_service.assert_lock_preconditions(case.id)


def test_lock_prevents_duplicate_lock(db_session: Session, seeded_case_with_proposal):
    """Test that locking already-locked case fails."""
    case = seeded_case_with_proposal
    
    # Create valid validation
    validation = PolicyValidation(
        case_id=case.id,
        validation_type="supplier_count",
        supplier_count=4,
        validation_result="valid",
        rule_snapshot='{"min": 3, "max": 6}',
        requirement_tags="REQ-DOMAIN-009"
    )
    db_session.add(validation)
    db_session.commit()
    
    # First lock succeeds
    agn3_service = AGN3Service(db_session)
    agn3_service.lock_longlist(case_id=case.id, actor_id="user-123")
    db_session.commit()
    
    # Second lock should fail
    with pytest.raises(ValueError, match="already locked"):
        agn3_service.lock_longlist(case_id=case.id, actor_id="user-456")


def test_lock_endpoint_returns_snapshot(client, auth_client, db_session, seeded_case_with_proposal):
    """Test POST /api/v1/cases/{caseId}/lock endpoint."""
    case = seeded_case_with_proposal
    
    # Create valid validation
    validation = PolicyValidation(
        case_id=case.id,
        validation_type="supplier_count",
        supplier_count=4,
        validation_result="valid",
        rule_snapshot='{"min": 3, "max": 6}',
        requirement_tags="REQ-DOMAIN-009"
    )
    db_session.add(validation)
    db_session.commit()
    
    # Lock via endpoint
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/lock",
        json={"actor_id": "user-123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["locked_longlist_id"] is not None
    assert data["lock_status"] == "locked"
    assert data["locked_by"] == "user-123"
    assert "locked_suppliers" in data
    assert data["total_suppliers"] > 0


def test_lock_endpoint_blocks_without_validation(client, auth_client, db_session, seeded_case_with_proposal):
    """Test lock endpoint blocks when validation missing."""
    case = seeded_case_with_proposal
    
    # Attempt lock without validation
    response = auth_client.post(
        f"/api/v1/cases/{case.id}/lock",
        json={"actor_id": "user-123"}
    )
    
    assert response.status_code == 409
    assert "must be validated" in response.json()["detail"]


def test_locked_supplier_preserves_rank_position(db_session: Session, seeded_case_with_proposal):
    """Test that locked suppliers preserve final rank positions."""
    case = seeded_case_with_proposal
    
    # Create valid validation
    validation = PolicyValidation(
        case_id=case.id,
        validation_type="supplier_count",
        supplier_count=4,
        validation_result="valid",
        rule_snapshot='{"min": 3, "max": 6}',
        requirement_tags="REQ-DOMAIN-009"
    )
    db_session.add(validation)
    db_session.commit()
    
    # Lock longlist
    agn3_service = AGN3Service(db_session)
    lock_result = agn3_service.lock_longlist(case_id=case.id, actor_id="user-123")
    db_session.commit()
    
    # Verify rank positions preserved
    for locked_supplier_data in lock_result["locked_suppliers"]:
        locked_supplier = db_session.query(LockedSupplier).filter_by(
            id=locked_supplier_data["locked_supplier_id"]
        ).first()
        assert locked_supplier is not None
        assert locked_supplier.final_rank_position == locked_supplier_data["final_rank_position"]


@pytest.fixture
def seeded_case_with_proposal(db_session: Session):
    """Create seeded case with longlist proposal for testing."""
    from app.models.longlist_proposal import LonglistProposal
    from app.models.need_case import NeedCase
    from app.models.normalized_need import NormalizedNeed
    from app.models.proposal_supplier import ProposalSupplier
    from app.models.supplier import Supplier
    
    # Create case
    case = NeedCase(
        case_number="CASE-TEST-LOCK-001",
        inbound_channel="email",
        workflow_state="longlist_pending",
        next_action="validate_count",
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
            supplier_code=f"SUP-LOCK-{i+1:03d}",
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
        proposal_status="draft",
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
    
    db_session.commit()
    return case
