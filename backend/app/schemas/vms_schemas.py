"""VMS handoff API request/response schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field


class VmsHandoffRequest(BaseModel):
    """Request schema for VMS handoff execution."""
    need_id: UUID
    classification_verdict: str = Field(..., pattern="^single_resource$")
    request_payload_json: dict


class VmsHandoffResponse(BaseModel):
    """Response schema for VMS handoff execution."""
    vms_handoff_id: UUID
    need_id: UUID
    handover_confirmation: bool
    vms_reference_id: str | None
    response_payload_json: dict | None
    sent_at: datetime
    correlation_id: UUID
    workflow_status: str

    model_config = ConfigDict(from_attributes=True)


class VmsHandoffListItem(BaseModel):
    """Single VMS handoff item for list view."""
    need_id: UUID
    classification_verdict: str
    handover_confirmation: bool
    vms_reference_id: str | None
    workflow_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VmsHandoffListResponse(BaseModel):
    """Response schema for VMS handoff list."""
    handoffs: list[VmsHandoffListItem]
    total: int


class ClassificationReviewRequest(BaseModel):
    """Request schema for ATS3 classification review."""
    review_decision: str = Field(..., pattern="^(approve|modify|reject)$")
    classification_verdict: str = Field(..., pattern="^(single_resource|it_service)$")
    classification_confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str | None = None
    exemplars_referenced: list[str] | None = None
    escalation_required: bool = False


class ClassificationReviewResponse(BaseModel):
    """Response schema for ATS3 classification review."""
    classification_review_id: UUID
    need_id: UUID
    review_decision: str
    classification_verdict: str
    classification_confidence: float
    rationale: str | None
    exemplars_referenced: list[str] | None
    escalation_required: bool
    next_workflow_status: str
    reviewed_by: str
    reviewed_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @computed_field
    @property
    def workflow_status(self) -> str:
        """Alias for backward compatibility."""
        return self.next_workflow_status
