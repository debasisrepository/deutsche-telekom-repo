"""Niche Research Router - ATS7 endpoint."""

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.research_schemas import NicheResearchRequest, NicheResearchResponse
from app.services.niche_research_service import NicheResearchService

router = APIRouter()


@router.post("/niche-research", response_model=NicheResearchResponse, status_code=201)
def research_niche_providers(
    request: NicheResearchRequest,
    x_correlation_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> NicheResearchResponse:
    """POST /api/v1/niche-research - Research niche providers (ATS7).

    Researches additional providers for niche capability gaps using governed sources
    when panel mapping (ATS6) identifies inadequate coverage. Only invoked when
    coverage_gap_flag=true and need classified as it_service.

    Candidates without governed source citations are rejected. Reviewers must
    accept/modify/reject candidates before they are eligible for longlist ranking.

    Args:
        request: Niche research request with need_id, capability_gap, approved sources
        x_correlation_id: Optional correlation ID header
        db: Database session

    Returns:
        NicheResearchResponse with research dossier and review requirement

    Raises:
        HTTPException 404: Need not found
        HTTPException 400: Invalid request, wrong need type, or no approved sources
        HTTPException 500: Research failure
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())

    try:
        service = NicheResearchService(db)
        response = service.research_niche_providers(
            need_id=request.need_id,
            capability_gap=request.capability_gap,
            approved_source_list=request.approved_source_list,
            correlation_id=correlation_id,
            existing_panel_matches=request.existing_panel_matches,
        )
        return response
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Niche research failed: {str(e)}",
        )
