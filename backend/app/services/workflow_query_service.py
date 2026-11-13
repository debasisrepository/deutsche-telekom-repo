"""Service for workflow query operations (audit trail retrieval)."""

import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.need_repository import NeedRepository

logger = logging.getLogger(__name__)


class WorkflowQueryService:
    """
    Service for querying workflow audit trails.

    Provides GET /api/v1/workflows/{need_id}/audit-events endpoint
    that returns audit_events array with audit_event_id, step_code,
    agent_code, tool_code, actor_type, actor_id, outcome, payload_ref,
    correlation_id, created_at.
    """

    def __init__(self, session: Session):
        self.session = session
        self.need_repo = NeedRepository(session)
        self.audit_repo = AuditEventRepository(session)

    def get_audit_events(
        self,
        need_id: UUID,
        correlation_id: str,
    ) -> dict:
        """
        Retrieve all audit events for a need.

        Args:
            need_id: Need ID to query
            correlation_id: Correlation ID for this query

        Returns:
            Dict with need_id, audit_events array, total_count, correlation_id

        Raises:
            HTTPException: If need not found
        """
        # Verify need exists
        need = self.need_repo.get_by_id(need_id)
        if not need:
            logger.error(f"Need {need_id} not found")
            raise HTTPException(status_code=404, detail=f"Need {need_id} not found")

        # Retrieve all audit events for this need
        audit_events = (
            self.session.query(AuditEvent)
            .filter(AuditEvent.need_id == need_id)
            .order_by(AuditEvent.created_at.asc())
            .all()
        )

        # Format audit events for response
        audit_event_items = [
            {
                "audit_event_id": event.id,
                "step_code": event.step_code,
                "agent_code": event.agent_code,
                "tool_code": event.tool_code,
                "actor_type": event.actor_type,
                "actor_id": event.actor_id,
                "outcome": event.outcome,
                "payload_ref": event.payload_ref,
                "correlation_id": event.correlation_id,
                "created_at": event.created_at,
            }
            for event in audit_events
        ]

        logger.info(f"Retrieved {len(audit_event_items)} audit events for need {need_id}")

        return {
            "need_id": need_id,
            "audit_events": audit_event_items,
            "total_count": len(audit_event_items),
            "correlation_id": correlation_id,
        }
