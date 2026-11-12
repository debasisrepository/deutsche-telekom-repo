"""Case Schemas - Request/response DTOs for case operations"""
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class CreateCaseRequest(BaseModel):
    """Request to create a new case from intake."""
    channel: str = Field(..., description="Inbound channel: rfp_document, email, phone_note, supplier_offer")
    title: str = Field(..., min_length=1, description="Need title")
    business_unit: str = Field(..., min_length=1, description="Requesting business unit")
    description: str = Field(..., min_length=1, description="Need description")
    artifact_type: str = Field(default="form_submission", description="Type of source artifact")
    artifact_ref: str = Field(default="", description="Reference to source artifact storage")
    submitted_via: str = Field(default="web", description="Submission method")


class SourceArtifactResponse(BaseModel):
    """Source artifact details."""
    id: int
    artifact_type: str
    storage_ref: str
    source_channel: str
    submitted_at: datetime
    
    model_config = {"from_attributes": True}


class NormalizedNeedResponse(BaseModel):
    """Normalized need record details."""
    id: int
    mandatory_fields: dict[str, Any]
    sourced_fields: dict[str, Any]
    derived_fields: dict[str, Any]
    completeness_score: float
    
    @field_validator("mandatory_fields", "sourced_fields", "derived_fields", mode="before")
    @classmethod
    def parse_json_fields(cls, v):
        """Parse JSON string fields if they are strings."""
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    model_config = {"from_attributes": True}


class VMSHandoffResponse(BaseModel):
    """VMS handoff details."""
    id: int
    case_id: int
    vms_reference_id: str
    handoff_status: str
    request_snapshot: dict[str, Any]
    handed_off_at: datetime
    
    @field_validator("request_snapshot", mode="before")
    @classmethod
    def parse_json_field(cls, v):
        """Parse JSON string field if it is a string."""
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    model_config = {"from_attributes": True}


class CaseListItem(BaseModel):
    """Case list item for intake queue."""
    id: int
    case_number: str
    inbound_channel: str
    workflow_state: str
    next_action: str
    final_classification: str | None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class CaseDetail(BaseModel):
    """Detailed case information."""
    id: int
    case_number: str
    inbound_channel: str
    workflow_state: str
    next_action: str
    final_classification: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    normalized_need: NormalizedNeedResponse | None = None
    source_artifacts: list[SourceArtifactResponse] = []
    vms_handoff: VMSHandoffResponse | None = None
    
    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    """Paginated case list response."""
    items: list[CaseListItem]
    total: int
    page: int
    page_size: int
