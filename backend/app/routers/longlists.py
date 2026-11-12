"""Longlists Router - Evidence retrieval and longlist management endpoints."""
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.repositories.case_repository import CaseRepository
from app.services.agents.agn2_service import AGN2Service
from app.services.agents.agn3_service import AGN3Service
from app.services.evidence.evidence_service import EvidenceService
from app.services.mapping.panel_mapping_service import PanelMappingService
from app.services.policy.longlist_policy_service import LonglistPolicyService

router = APIRouter()


class AdjustmentRequest(BaseModel):
    """Request schema for supplier adjustment."""
    supplier_id: int
    change_type: str  # 'add' or 'remove'
    rationale: str | None = None


@router.get("/cases/{caseId}/evidence")
def get_case_evidence(
    caseId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Get historical evidence for a case.
    
    Returns evidence items with supplier details, citations, and evidence summaries.
    Evidence must be retrieved before longlist generation can proceed.
    """
    # Verify case exists
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")
    
    # Get evidence service
    evidence_service = EvidenceService(db)
    
    # List evidence for case
    evidence_list = evidence_service.list_evidence(caseId)
    
    return {
        "case_id": caseId,
        "case_number": case.case_number,
        "evidence_items": evidence_list,
        "total": len(evidence_list)
    }


@router.get("/cases/{caseId}/mapping")
def get_case_mapping(
    caseId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Get panel and functional-group mappings for a case.
    
    Returns proposed mappings with rationale inputs for review.
    Mappings determine which supplier panels are eligible for the case.
    """
    # Verify case exists
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")
    
    # Get mapping service
    mapping_service = PanelMappingService(db)
    
    # List mappings for case
    mappings = mapping_service.list_mappings(caseId)
    
    return {
        "case_id": caseId,
        "case_number": case.case_number,
        "mappings": mappings,
        "total": len(mappings)
    }


@router.post("/cases/{caseId}/longlist-proposals")
def create_longlist_proposal(
    caseId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Generate ranked longlist proposal for a case.
    
    Creates a new version of the supplier longlist with ranked recommendations
    based on historical evidence and panel mappings. Each supplier includes
    rank position, ranking score, and citation completeness flag.
    
    Returns the proposal with ranked suppliers in {items, total} wrapper format.
    """
    # Verify case exists
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")
    
    # Get confirmed attributes from normalized need
    if not case.normalized_need:
        raise HTTPException(status_code=400, detail="Case has no normalized need data")
    
    try:
        confirmed_attributes = json.loads(case.normalized_need.mandatory_fields)
    except (json.JSONDecodeError, AttributeError):
        confirmed_attributes = {}
    
    # Get mapping info if available
    mapping_service = PanelMappingService(db)
    mappings = mapping_service.list_mappings(caseId)
    mapping_info = {"mappings": mappings} if mappings else None
    
    # Generate longlist proposal via AGN2
    agn2_service = AGN2Service(db)
    proposal_result = agn2_service.generate_ranked_longlist(
        case_id=caseId,
        confirmed_attributes=confirmed_attributes,
        mapping_info=mapping_info,
        agent_run_id=f"agn2-run-{caseId}"
    )
    
    # Return in standard {items, total} wrapper format
    return {
        "items": proposal_result["suppliers"],
        "total": proposal_result["total_suppliers"],
        "proposal_id": proposal_result["proposal_id"],
        "version_no": proposal_result["version_no"],
        "proposal_status": proposal_result["proposal_status"],
        "created_at": proposal_result["created_at"]
    }


@router.post("/cases/{caseId}/adjustments")
def create_adjustment(
    caseId: int,
    request: AdjustmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Capture supplier adjustment (add or remove).
    
    Records business-unit add/remove actions with actor, timestamp, rationale,
    and recalculates resulting supplier count. Adjustment history remains visible
    before and after finalization.
    
    Request body:
        supplier_id: Supplier being added or removed
        change_type: 'add' or 'remove'
        rationale: Business justification (optional)
    
    Returns adjustment record with resulting_supplier_count.
    """
    # Verify case exists
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")
    
    # Create adjustment via AGN3
    agn3_service = AGN3Service(db)
    try:
        adjustment_result = agn3_service.capture_adjustment(
            case_id=caseId,
            supplier_id=request.supplier_id,
            change_type=request.change_type,
            rationale=request.rationale,
            actor_id=str(current_user.id)
        )
        db.commit()
        return adjustment_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cases/{caseId}/validations/supplier-count")
def validate_supplier_count(
    caseId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """Validate supplier count against the 3-6 rule.
    
    Invokes AGN5/TOL4 adapter to validate supplier count and creates a
    policy_validation record. Blocks finalization when validation result
    is not 'valid'.
    
    Validation results:
        - valid: 3-6 suppliers (target band)
        - invalid_low: < 3 suppliers (blocks finalization)
        - invalid_high: > 6 suppliers (flags against target-band rule)
    
    Returns validation record with supplier_count, validation_result, and rule_snapshot.
    """
    # Verify case exists
    case_repo = CaseRepository(db)
    case = case_repo.get_by_id(caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")
    
    # Validate supplier count via policy service
    policy_service = LonglistPolicyService(db)
    try:
        validation_result = policy_service.validate_supplier_count(caseId)
        db.commit()
        return validation_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
