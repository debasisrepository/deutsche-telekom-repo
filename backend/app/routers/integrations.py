"""Integration Routers - VMS Handoff and External System Triggers"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.common_schemas import MessageResponse
from app.services.agents.agn3_service import AGN3Service
from app.services.policy.longlist_policy_service import LonglistPolicyService
from app.services.workflow.orchestrator_service import WorkflowOrchestratorService

router = APIRouter()


class LockRequest(BaseModel):
    """Request schema for longlist lock."""
    actor_id: str | None = None


class DispatchRequest(BaseModel):
    """Request schema for tender dispatch."""
    actor_id: str | None = None


@router.post("/cases/{caseId}/vms-handoff", response_model=MessageResponse)
def trigger_vms_handoff(
    caseId: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MessageResponse:
    """
    Trigger VMS handoff for single-resource case (REQ-INT-001, FR-010).
    
    Preconditions:
    - Case must be classified as single_resource
    - Classification must be confirmed
    
    Effects:
    - Creates vms_handoff record with VMS reference ID
    - Updates case workflow_state to routed_to_vms
    - Terminates supplier-selection workflow
    - Records audit trail
    
    Args:
        caseId: Case identifier
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Success message with VMS reference ID
        
    Raises:
        404: Case not found
        409: Case not eligible for VMS handoff
    """
    orchestrator = WorkflowOrchestratorService(db)
    
    try:
        case = orchestrator.route_single_resource_case(
            case_id=caseId,
            reviewer_id=current_user.id
        )
        
        # Get VMS handoff record
        from app.models.vms_handoff import VMSHandoff
        vms_handoff = db.query(VMSHandoff).filter_by(case_id=caseId).first()
        
        if vms_handoff:
            return MessageResponse(
                message=f"Case {case.case_number} routed to VMS. VMS Reference: {vms_handoff.vms_reference_id}"
            )
        else:
            return MessageResponse(
                message=f"Case {case.case_number} routed to VMS"
            )
    
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="VMS handoff failed")


@router.post("/cases/{caseId}/lock")
def lock_longlist(
    caseId: int,
    request: LockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Lock longlist before tender dispatch (REQ-DOMAIN-010, FR-024).
    
    Creates immutable snapshot of finalized supplier set.
    Once locked, the supplier list cannot be altered without explicit unlock.
    
    Preconditions:
    - Latest supplier-count validation must be 'valid' (3-6 suppliers)
    
    Request body:
        actor_id: User ID performing lock (optional, defaults to current_user.id)
    
    Returns lock record with locked_longlist_id and locked suppliers.
    """
    # Determine actor ID
    actor_id = request.actor_id or str(current_user.id)
    
    # Assert lock preconditions
    policy_service = LonglistPolicyService(db)
    try:
        policy_service.assert_lock_preconditions(caseId)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    # Lock longlist via AGN3
    agn3_service = AGN3Service(db)
    try:
        lock_result = agn3_service.lock_longlist(
            case_id=caseId,
            actor_id=actor_id
        )
        db.commit()
        return lock_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cases/{caseId}/dispatch")
def dispatch_tender(
    caseId: int,
    request: DispatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Dispatch tender to finalized suppliers (REQ-INT-004, FR-026).
    
    Sends or registers dispatch to every supplier on the locked longlist.
    Records per-supplier delivery outcomes and overall dispatch status.
    
    Preconditions:
    - Case must have locked longlist
    
    Request body:
        actor_id: User ID performing dispatch (optional, defaults to current_user.id)
    
    Returns dispatch record with dispatch_batch_ref, dispatch_status,
    and recipients array with per-supplier delivery outcomes.
    
    Dispatch status:
        - success: All suppliers received tender successfully
        - partial_failure: Some suppliers received, some failed
        - failed: No suppliers received tender
    """
    # Determine actor ID
    actor_id = request.actor_id or str(current_user.id)
    
    # Assert dispatch preconditions
    policy_service = LonglistPolicyService(db)
    try:
        policy_service.assert_dispatch_preconditions(caseId)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    # Dispatch tender via AGN3
    agn3_service = AGN3Service(db)
    try:
        dispatch_result = agn3_service.dispatch_tender(
            case_id=caseId,
            actor_id=actor_id
        )
        db.commit()
        return dispatch_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
