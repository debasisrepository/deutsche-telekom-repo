"""Panel Mappings Router - ATS6 endpoint."""

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.panel_schemas import PanelMappingRequest, PanelMappingResponse
from app.services.panel_mapping_service import PanelMappingService

router = APIRouter()


@router.post("/panel-mappings", response_model=PanelMappingResponse, status_code=200)
def map_need_to_panels(
    request: PanelMappingRequest,
    x_correlation_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> PanelMappingResponse:
    """POST /api/v1/panel-mappings - Map need to pre-selection panels (ATS6).

    Maps a classified need to candidate suppliers from the panel and functional-group
    catalog. Returns candidate suppliers with panel provenance and coverage gap flag
    that triggers ATS7 niche research when true.

    Args:
        request: Panel mapping request with need_id and need_category
        x_correlation_id: Optional correlation ID header
        db: Database session

    Returns:
        PanelMappingResponse with candidate suppliers and coverage gap flag

    Raises:
        HTTPException 404: Need not found
        HTTPException 400: Invalid request or need state
        HTTPException 500: Mapping failure
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())

    try:
        service = PanelMappingService(db)
        response = service.map_need_to_panels(
            need_id=request.need_id,
            need_category=request.need_category,
            correlation_id=correlation_id,
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
            detail=f"Panel mapping failed: {str(e)}",
        )
