"""Review API router."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.review_schemas import AttributeReviewRequest, AttributeReviewResponse
from app.schemas.vms_schemas import ClassificationReviewRequest, ClassificationReviewResponse
from app.services.classification_decision_service import ClassificationDecisionService
from app.services.need_review_service import NeedReviewService

router = APIRouter()


def get_current_reviewer(request: Request) -> str:
    """
    Extract reviewer_id from authenticated user.
    
    Reads from request.state.user set by auth middleware.
    Falls back to default reviewer for development when auth is not enforced.
    """
    if hasattr(request.state, "user") and request.state.user:
        # Extract email from JWT payload
        return request.state.user.get("sub", "reviewer@example.com")
    # Fallback for development when auth middleware allows unauthenticated access
    return "reviewer@example.com"


@router.post("/needs/{need_id}/attributes", response_model=AttributeReviewResponse)
def review_need_attributes(
    need_id: UUID,
    request: AttributeReviewRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/reviews/needs/{need_id}/attributes

    ATS2: Capture reviewer decision on extracted attributes.
    Supports approve, modify, or reject. Persists reviewed state,
    logs decision, advances workflow status.
    """
    reviewer_id = get_current_reviewer(http_request)

    service = NeedReviewService(db)

    try:
        response = service.review_attributes(need_id, request, reviewer_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/needs/{need_id}/classification", response_model=ClassificationReviewResponse)
def review_need_classification(
    need_id: UUID,
    request: ClassificationReviewRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/reviews/needs/{need_id}/classification

    ATS3: Capture reviewer decision on classification.
    Enforces allowed verdict enum (single_resource | it_service),
    logs decision with rationale and exemplars, advances workflow status.
    Low-confidence cases held for review, never auto-routed.
    """
    reviewer_id = get_current_reviewer(http_request)

    service = ClassificationDecisionService(db)

    try:
        response = service.review_classification(need_id, request, reviewer_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
