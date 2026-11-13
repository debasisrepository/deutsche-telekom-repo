import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.governance_schemas import (
    LonglistAdjustmentRequest,
    LonglistAdjustmentResponse,
    LonglistLockRequest,
    LonglistLockResponse,
    SupplierCountValidationRequest,
    SupplierCountValidationResponse,
)
from app.services.longlist_adjustment_service import LonglistAdjustmentService
from app.services.longlist_lock_service import LonglistLockService
from app.services.supplier_count_validation_service import (
    SupplierCountValidationService,
)

router = APIRouter()


@router.post("/{proposal_id}/validate-count", response_model=SupplierCountValidationResponse, status_code=200)
def validate_supplier_count(
    proposal_id: str,
    request: SupplierCountValidationRequest,
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Validate longlist supplier count against business rules (ATS9).

    Enforces the 3-6 supplier count rule:
    - Pass: 3 <= count <= 6
    - Fail: count < 3 or count > 6

    Returns validation verdict and violations if any.
    """
    service = SupplierCountValidationService(db)

    return service.validate_count(
        proposal_or_longlist_id=proposal_id,
        supplier_ids=request.supplier_ids,
        correlation_id=x_correlation_id,
    )


@router.post("/{longlist_id}/adjustments", response_model=LonglistAdjustmentResponse, status_code=201)
def capture_longlist_adjustment(
    longlist_id: str,
    request: LonglistAdjustmentRequest,
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Capture business-unit longlist adjustments (ATS10).

    Validates supplier existence, records adjustment with reason,
    updates suppliers list, reruns ATS9 validation, and returns
    updated suppliers with validation verdict and change history count.
    """
    from datetime import UTC, datetime
    
    correlation_id = x_correlation_id or str(uuid.uuid4())
    service = LonglistAdjustmentService(db)

    return service.capture_adjustment(
        longlist_id=uuid.UUID(longlist_id),
        supplier_id=request.supplier_id,
        action=request.action,
        reason=request.reason,
        actor=request.actor,
        timestamp=request.timestamp or datetime.now(UTC),
        correlation_id=correlation_id,
    )


@router.post("/{id}/lock", response_model=LonglistLockResponse, status_code=200)
def lock_longlist(
    id: str,
    request: LonglistLockRequest,
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Finalize and lock longlist immutably (ATS11).

    Accepts either a proposal_id or longlist_id. If proposal_id is provided,
    creates or finds the associated longlist before locking.

    Revalidates supplier set, persists immutable Longlist with locked=true,
    writes audit event, marks workflow locked. Commit fails if validation
    verdict not pass.

    Returns longlist_id, need_id, suppliers, locked, locked_at, change_history,
    validation_count.
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())
    service = LonglistLockService(db)

    return service.lock_by_id(
        id=uuid.UUID(id),
        expected_validation_verdict=request.expected_validation_verdict,
        supplier_ids=request.supplier_ids,
        finalized_by=request.finalized_by,
        correlation_id=correlation_id,
    )
