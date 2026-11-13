"""Schemas for audit event operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditEventItem(BaseModel):
    """Individual audit event."""
    audit_event_id: UUID
    step_code: str
    agent_code: Optional[str] = None
    tool_code: Optional[str] = None
    actor_type: str
    actor_id: Optional[str] = None
    outcome: str
    payload_ref: Optional[str] = None
    correlation_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditEventsResponse(BaseModel):
    """Response schema for audit events query."""
    need_id: UUID
    audit_events: List[AuditEventItem]
    total_count: int
    correlation_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
