"""Intake API router."""
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.need_repository import NeedRepository
from app.schemas.intake_schemas import NeedDetailResponse, NeedIntakeRequest, NeedIntakeResponse
from app.services.need_ingestion_service import NeedIngestionService

router = APIRouter()


@router.post("/needs", response_model=NeedIntakeResponse, status_code=201)
def create_need(
    request: NeedIntakeRequest,
    x_correlation_id: str | None = Header(None, alias="X-Correlation-Id"),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/intake/needs

    ATS1: Ingest and normalize incoming need from approved channels.
    Validates schema, masks PII, creates Need record, writes audit event.
    """
    service = NeedIngestionService(db)

    try:
        correlation_id = x_correlation_id or str(uuid.uuid4())
        response = service.ingest_need(request, correlation_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/needs", response_model=list[NeedDetailResponse])
def list_needs(
    db: Session = Depends(get_db),
    limit: int = 100,
):
    """
    GET /api/v1/intake/needs

    Retrieve list of needs for intake monitoring table.
    """
    repo = NeedRepository(db)
    needs = repo.list_all(limit=limit)
    return [NeedDetailResponse.model_validate(need) for need in needs]


@router.get("/needs/{need_id}", response_model=NeedDetailResponse)
def get_need(
    need_id: UUID,
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/intake/needs/{need_id}

    Retrieve Need workflow state and normalized intake view.
    """
    repo = NeedRepository(db)
    need = repo.get_by_id(need_id)

    if not need:
        raise HTTPException(status_code=404, detail="Need not found")

    return NeedDetailResponse.model_validate(need)
