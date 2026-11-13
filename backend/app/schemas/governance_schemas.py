from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SupplierCountValidationRequest(BaseModel):
    """Request schema for supplier count validation (ATS9)."""
    proposal_or_longlist_id: Optional[str] = Field(None, description="Proposal or longlist ID to validate (optional when provided in path)")
    supplier_ids: List[str] = Field(..., description="List of supplier IDs to validate count")


class SupplierCountValidationResponse(BaseModel):
    """Response schema for supplier count validation (ATS9)."""
    proposal_id: str
    supplier_count: int
    validation_verdict: str = Field(..., pattern="^(pass|fail)$")
    violations: List[str]
    validated_at: datetime
    correlation_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LonglistAdjustmentRequest(BaseModel):
    """Request schema for longlist adjustment capture (ATS10)."""
    longlist_id: Optional[str] = Field(None, description="Longlist ID to adjust (optional when provided in path)")
    supplier_id: str = Field(..., description="Supplier ID to add or remove")
    action: str = Field(..., pattern="^(add|remove)$", description="Add or remove action")
    reason: str = Field(..., description="Reason for adjustment")
    actor: str = Field(..., description="Actor making the adjustment")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the adjustment (defaults to now if not provided)")


class LonglistAdjustmentResponse(BaseModel):
    """Response schema for longlist adjustment capture (ATS10)."""
    adjustment_id: UUID
    longlist_id: UUID
    updated_suppliers: List[str]
    validation_verdict: str = Field(..., pattern="^(pass|fail)$")
    change_history_count: int
    correlation_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LonglistLockRequest(BaseModel):
    """Request schema for longlist lock (ATS11)."""
    expected_validation_verdict: str = Field(..., pattern="^pass$", description="Must be 'pass'")
    supplier_ids: List[str] = Field(..., description="Supplier IDs to lock")
    finalized_by: str = Field(..., description="User who finalized the longlist")


class LonglistLockResponse(BaseModel):
    """Response schema for longlist lock (ATS11)."""
    longlist_id: UUID
    need_id: UUID
    suppliers: List[str]
    locked: bool
    locked_at: datetime
    change_history: List[dict]
    validation_count: int
    correlation_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
