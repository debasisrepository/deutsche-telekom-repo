"""Reviews Router - Extraction and classification review endpoints"""
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.classification_result import ClassificationResult
from app.models.need_case import NeedCase
from app.models.user import User
from app.schemas.review_schemas import (
    ClassificationReviewDecisionRequest,
    ExtractionReviewDecisionRequest,
    ReviewDecisionResponse,
)
from app.services.reviews.hitl_service import HITLService

router = APIRouter(tags=["reviews"])


@router.post("/{caseId}/reviews/extraction", response_model=ReviewDecisionResponse)
def apply_extraction_review_decision(
    caseId: int,
    request: ExtractionReviewDecisionRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> ReviewDecisionResponse:
    """
    Apply extraction review decision (approve, edit, reject).
    
    Per REQ-DOMAIN-003, reviewer can:
    - Approve extracted attributes without modification
    - Edit one or more extracted attributes and save the corrected set
    - Reject the extraction result and require rework
    
    System logs the chosen action and resulting attribute set.
    """
    # Verify case exists
    case = db.get(NeedCase, caseId)
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")
    
    # Get pending extraction review for this case
    from app.repositories.review_repository import ReviewRepository
    
    review_repo = ReviewRepository(db)
    reviews = review_repo.get_by_case_and_type(
        case_id=caseId,
        review_type="extraction",
        status="pending"
    )
    
    if not reviews:
        raise HTTPException(
            status_code=404,
            detail=f"No pending extraction review found for case {caseId}"
        )
    
    review = reviews[0]
    
    # Validate decision
    valid_decisions = ["approve", "edit", "reject"]
    if request.decision not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision: {request.decision}. Must be one of {valid_decisions}"
        )
    
    # For 'edit' decision, validate edited_attributes provided
    if request.decision == "edit" and request.edited_attributes is None:
        raise HTTPException(
            status_code=400,
            detail="edited_attributes required for 'edit' decision"
        )
    
    # Apply decision via HITL service
    hitl_service = HITLService(db)
    
    try:
        updated_review = hitl_service.apply_decision(
            review_id=review.id,
            decision=request.decision,
            reviewer_id=current_user.id,
            edited_payload=request.edited_attributes
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    db.commit()
    
    # Get updated case state
    db.refresh(case)
    
    return ReviewDecisionResponse(
        review_id=updated_review.id,
        case_id=updated_review.case_id,
        review_type=updated_review.review_type,
        status=updated_review.status,
        decision=updated_review.decision or "",
        reviewer_id=updated_review.reviewer_id or 0,
        reviewed_at=updated_review.reviewed_at or updated_review.created_at,
        next_workflow_state=case.workflow_state,
        next_action=case.next_action
    )


@router.post("/{caseId}/reviews/classification", response_model=ReviewDecisionResponse)
def apply_classification_review_decision(
    caseId: int,
    request: ClassificationReviewDecisionRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> ReviewDecisionResponse:
    """
    Apply classification review decision (confirm, override).
    
    Per REQ-DOMAIN-005, reviewer can:
    - Accept the classification verdict
    - Override the verdict and specify the corrected path
    
    System records the original verdict, override action, and final confirmed classification.
    Final confirmed classification controls downstream routing.
    """
    # Verify case exists
    case = db.get(NeedCase, caseId)
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")
    
    # Get pending classification review for this case
    from app.repositories.review_repository import ReviewRepository
    
    review_repo = ReviewRepository(db)
    reviews = review_repo.get_by_case_and_type(
        case_id=caseId,
        review_type="classification",
        status="pending"
    )
    
    if not reviews:
        raise HTTPException(
            status_code=404,
            detail=f"No pending classification review found for case {caseId}"
        )
    
    review = reviews[0]
    
    # Validate decision
    valid_decisions = ["confirm", "override"]
    if request.decision not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision: {request.decision}. Must be one of {valid_decisions}"
        )
    
    # For 'override' decision, validate confirmed_verdict provided
    if request.decision == "override":
        if request.confirmed_verdict is None:
            raise HTTPException(
                status_code=400,
                detail="confirmed_verdict required for 'override' decision"
            )
        
        # Validate confirmed_verdict value
        valid_verdicts = ["single_resource", "it_service"]
        if request.confirmed_verdict not in valid_verdicts:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid verdict: {request.confirmed_verdict}. Must be one of {valid_verdicts}"
            )
    
    # Parse generated payload to get AI verdict
    generated_payload = json.loads(review.generated_payload) if review.generated_payload else {}
    ai_verdict = generated_payload.get("ai_verdict", "it_service")
    confidence_score = generated_payload.get("confidence_score", 0.0)
    rationale_inputs = generated_payload.get("rationale_inputs", {})
    
    # Determine final verdict
    if request.decision == "confirm":
        final_verdict = ai_verdict
        overridden = False
        decision_for_service = "approve"
        override_payload = None
    else:  # override
        final_verdict = request.confirmed_verdict
        overridden = True
        decision_for_service = "override"
        override_payload = {
            "ai_verdict": ai_verdict,
            "confirmed_verdict": final_verdict,
            "overridden": True
        }
    
    # Apply decision via HITL service
    hitl_service = HITLService(db)
    
    try:
        updated_review = hitl_service.apply_decision(
            review_id=review.id,
            decision=decision_for_service,
            reviewer_id=current_user.id,
            edited_payload=override_payload
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create or update classification_result record
    classification_result = db.query(ClassificationResult).filter_by(case_id=caseId).first()
    
    if classification_result is None:
        classification_result = ClassificationResult(
            case_id=caseId,
            ai_verdict=ai_verdict,
            confirmed_verdict=final_verdict,
            confidence_score=confidence_score,
            rationale_inputs=json.dumps(rationale_inputs),
            overridden=overridden,
            requirement_tags="REQ-DOMAIN-005"
        )
        db.add(classification_result)
    else:
        classification_result.confirmed_verdict = final_verdict
        classification_result.overridden = overridden
    
    # Update case final_classification
    case.final_classification = final_verdict
    
    db.commit()
    
    # Get updated case state
    db.refresh(case)
    
    return ReviewDecisionResponse(
        review_id=updated_review.id,
        case_id=updated_review.case_id,
        review_type=updated_review.review_type,
        status=updated_review.status,
        decision=updated_review.decision or "",
        reviewer_id=updated_review.reviewer_id or 0,
        reviewed_at=updated_review.reviewed_at or updated_review.created_at,
        next_workflow_state=case.workflow_state,
        next_action=case.next_action
    )
