"""Router for tender dispatch operations (ATS12)."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tender_dispatch import TenderDispatch
from app.schemas.dispatch_schemas import (
    TenderDispatchRequest,
    TenderDispatchResponse,
    TenderDispatchListResponse,
)
from app.services.tender_dispatch_service import TenderDispatchService

router = APIRouter()


@router.get("/dispatches", response_model=list[TenderDispatchListResponse])
def list_tender_dispatches(
    db: Session = Depends(get_db),
    limit: int = 100,
):
    """
    GET /api/v1/tender-dispatches
    
    Retrieve list of tender dispatches for monitoring.
    """
    dispatches = db.query(TenderDispatch).order_by(TenderDispatch.created_at.desc()).limit(limit).all()
    return [TenderDispatchListResponse.model_validate(dispatch) for dispatch in dispatches]


@router.post("/dispatch", response_model=TenderDispatchResponse, status_code=201)
def dispatch_tender(
    request: TenderDispatchRequest,
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Dispatch tender to all suppliers on locked longlist (ATS12).

    Blocks dispatch when longlist unlocked/empty/invalid contacts.
    Builds tender package from locked longlist, dispatches to every
    supplier via TOL6, records per-supplier dispatch_status
    (pending|retrying|delivered|failed|escalated), retry_count,
    delivery_confirmation_ref, tender_package_ref, escalation_opened,
    last_attempt_at.

    Returns dispatch_batch_id, longlist_id, supplier_dispatches array.
    Idempotent retry for failures, escalates after retry exhaustion.
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())
    service = TenderDispatchService(db)

    # Convert supplier_contacts to list of dicts
    supplier_contacts = [
        {
            "supplier_id": contact.supplier_id,
            "contact_email": contact.contact_email,
            "contact_name": contact.contact_name,
        }
        for contact in request.supplier_contacts
    ]

    return service.dispatch_tender(
        longlist_id=uuid.UUID(request.longlist_id),
        tender_template=request.tender_template,
        supplier_contacts=supplier_contacts,
        correlation_id=correlation_id,
    )
