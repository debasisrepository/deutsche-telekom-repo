"""Schemas for tender dispatch operations (ATS12)."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SupplierContactItem(BaseModel):
    """Supplier contact information for tender dispatch."""
    supplier_id: str = Field(..., description="Supplier ID")
    contact_email: str = Field(..., description="Contact email for tender delivery")
    contact_name: Optional[str] = Field(None, description="Contact person name")


class TenderDispatchRequest(BaseModel):
    """Request schema for tender dispatch (ATS12)."""
    longlist_id: str = Field(..., description="Locked longlist ID")
    tender_template: str = Field(..., description="Tender template reference")
    supplier_contacts: List[SupplierContactItem] = Field(..., description="Supplier contact information")


class SupplierDispatchDetail(BaseModel):
    """Individual supplier dispatch outcome."""
    dispatch_id: UUID
    supplier_id: str
    tender_package_ref: str
    dispatch_status: str = Field(..., pattern="^(pending|retrying|delivered|failed|escalated)$")
    retry_count: int
    delivery_confirmation_ref: Optional[str] = None
    escalation_opened: bool
    last_attempt_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TenderDispatchResponse(BaseModel):
    """Response schema for tender dispatch (ATS12)."""
    dispatch_batch_id: str
    longlist_id: UUID
    supplier_dispatches: List[SupplierDispatchDetail]
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


class TenderDispatchListResponse(BaseModel):
    """Response schema for tender dispatch list."""
    id: UUID
    longlist_id: UUID
    dispatch_batch_id: str
    supplier_id: str
    supplier_contact: str
    dispatch_status: str
    retry_count: int
    delivery_confirmation_ref: Optional[str] = None
    error_detail: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
