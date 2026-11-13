"""Intake API request/response schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.review_schemas import NeedAttributesRequest


class NeedIntakeRequest(BaseModel):
    """Request schema for need intake submission."""
    business_unit_id: str = Field(..., max_length=100)
    channel_type: str = Field(..., pattern="^(rfp|email|phone|supplier_offer)$")
    raw_artifact_ref: str | None = None
    normalized_payload_json: str | None = None
    need_attributes: NeedAttributesRequest | None = None


class NeedIntakeResponse(BaseModel):
    """Response schema for need intake submission."""
    need_id: UUID
    status: str
    correlation_id: str

    model_config = ConfigDict(from_attributes=True)


class NeedDetailResponse(BaseModel):
    """Response schema for need detail retrieval."""
    id: UUID
    business_unit_id: str
    channel_type: str
    arrival_timestamp: datetime
    raw_artifact_ref: str | None
    normalized_payload_json: str | None
    status: str
    classification_verdict: str | None
    classification_confidence: float | None
    evidence_limited_flag: bool
    correlation_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
