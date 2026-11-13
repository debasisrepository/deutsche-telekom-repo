from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.evidence_schemas import EvidenceQueryRequest, EvidenceQueryResponse
from app.services.supplier_evidence_service import SupplierEvidenceService

router = APIRouter()


@router.post("/queries", response_model=EvidenceQueryResponse, status_code=200)
def query_evidence(
    request: EvidenceQueryRequest,
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Query historical supplier and project evidence (ATS5).

    Retrieves evidence from TOL2 when available, gracefully degrades to seed data.
    Sets evidence_limited_flag when using fallback.
    Never fabricates suppliers or evidence when unavailable.
    """
    service = SupplierEvidenceService(db)

    return service.query_evidence(
        need_id=request.need_id,
        service_type=request.service_type,
        required_skills=request.required_skills,
        business_unit_id=request.business_unit_id,
        panel_filters=request.panel_filters,
        correlation_id=x_correlation_id,
    )
