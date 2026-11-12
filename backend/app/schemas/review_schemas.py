"""Review Schemas - Request/response models for HITL review endpoints"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ExtractionReviewDecisionRequest(BaseModel):
    """Request body for extraction review decision"""
    decision: str  # approve, edit, reject
    edited_attributes: dict[str, Any] | None = None


class ClassificationReviewDecisionRequest(BaseModel):
    """Request body for classification review decision"""
    decision: str  # confirm, override
    confirmed_verdict: str | None = None  # single_resource or it_service (required for override)


class ReviewDecisionResponse(BaseModel):
    """Response after applying review decision"""
    review_id: int
    case_id: int
    review_type: str
    status: str
    decision: str
    reviewer_id: int
    reviewed_at: datetime
    next_workflow_state: str
    next_action: str
    
    model_config = ConfigDict(from_attributes=True)


class HITLReviewResponse(BaseModel):
    """Response model for HITL review record"""
    id: int
    case_id: int
    review_type: str
    status: str
    assigned_role: str | None
    decision: str | None
    reviewer_id: int | None
    reviewed_at: datetime | None
    generated_payload: str | None
    final_payload: str | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
