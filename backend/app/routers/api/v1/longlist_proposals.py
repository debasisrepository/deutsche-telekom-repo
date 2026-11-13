"""Longlist Proposals API router - ATS8 endpoint."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.proposal_schemas import LonglistProposalRequest, LonglistProposalResponse
from app.services.longlist_proposal_service import LonglistProposalService

router = APIRouter()


@router.post("", response_model=LonglistProposalResponse, status_code=201)
def create_longlist_proposal(
    request: LonglistProposalRequest,
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Generate ranked longlist proposal (ATS8).

    Args:
        request: Proposal generation request
        x_correlation_id: Optional correlation ID header
        db: Database session

    Returns:
        LonglistProposalResponse with ranked suppliers

    Raises:
        HTTPException: If validation fails or need not found
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())
    service = LonglistProposalService(db)

    response = service.generate_proposal(
        need_id=uuid.UUID(request.need_id),
        matched_panels=request.matched_panels,
        evidence_items=request.evidence_items,
        approved_niche_candidates=request.approved_niche_candidates or [],
        correlation_id=correlation_id,
    )

    return response
