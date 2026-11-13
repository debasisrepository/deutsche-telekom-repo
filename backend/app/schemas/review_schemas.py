"""Review API request/response schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field


class NeedAttributesRequest(BaseModel):
    """Request schema for need attributes (used in review)."""
    service_type: str | None = Field(None, max_length=200)
    scope_description: str | None = None
    estimated_volume_duration: str | None = Field(None, max_length=500)
    required_skills: str | None = None  # JSON string
    budget_indication: str | None = Field(None, max_length=200)
    delivery_location: str | None = Field(None, max_length=500)
    field_confidence: str | None = None  # JSON string


class AttributeReviewRequest(BaseModel):
    """Request schema for ATS2 attribute review."""
    review_decision: str = Field(..., pattern="^(approve|modify|reject)$")
    need_attributes: NeedAttributesRequest | None = None
    reviewer_notes: str | None = None


class AttributeReviewResponse(BaseModel):
    """Response schema for ATS2 attribute review."""
    need_id: UUID
    review_decision: str
    next_workflow_status: str
    need_attributes_id: UUID | None
    need_attributes: "NeedAttributesResponse | None" = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @computed_field
    @property
    def next_status(self) -> str:
        """Alias for backward compatibility."""
        return self.next_workflow_status


class NeedAttributesResponse(BaseModel):
    """Response schema for need attributes."""
    id: UUID
    need_id: UUID
    service_type: str | None
    scope_description: str | None
    estimated_volume_duration: str | None
    required_skills: str | None
    budget_indication: str | None
    delivery_location: str | None
    field_confidence: str | None
    schema_valid: bool
    review_status: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
