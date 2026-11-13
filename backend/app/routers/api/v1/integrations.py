"""Integrations API router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.vms_schemas import VmsHandoffRequest, VmsHandoffResponse, VmsHandoffListResponse
from app.services.vms_handoff_service import VmsHandoffService

router = APIRouter()


@router.post("/vms/handoffs", response_model=VmsHandoffResponse, status_code=201)
def execute_vms_handoff(
    request: VmsHandoffRequest,
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/integrations/vms/handoffs

    ATS4: Execute VMS handoff for reviewed single-resource cases.
    Calls TOL5 VMS connector, records handover_confirmation and vms_reference_id,
    marks workflow status as vms_routed_terminal, blocks ATS5-ATS12.
    Failed handoff recorded with error status and escalation.
    """
    service = VmsHandoffService(db)

    try:
        response = service.execute_handoff(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/vms/handoffs", response_model=VmsHandoffListResponse)
def list_vms_handoffs(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/integrations/vms/handoffs

    List all VMS handoffs with handoff status and workflow status.
    Returns handoffs ordered by created_at descending.
    """
    service = VmsHandoffService(db)
    
    try:
        handoffs = service.list_handoffs(limit=limit)
        return VmsHandoffListResponse(handoffs=handoffs, total=len(handoffs))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
