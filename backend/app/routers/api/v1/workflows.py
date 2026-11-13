"""Router for workflow query operations (audit trail retrieval)."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.audit_schemas import AuditEventsResponse
from app.services.workflow_query_service import WorkflowQueryService

router = APIRouter()


@router.get("/{need_id}/audit-events", response_model=AuditEventsResponse, status_code=200)
def get_audit_events(
    need_id: str,
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Retrieve audit trail for a workflow need.

    Returns audit_events array with audit_event_id, step_code, agent_code,
    tool_code, actor_type, actor_id, outcome, payload_ref, correlation_id,
    created_at.
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())
    service = WorkflowQueryService(db)

    return service.get_audit_events(
        need_id=uuid.UUID(need_id),
        correlation_id=correlation_id,
    )
