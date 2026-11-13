"""Audit event service."""
import uuid
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.repositories.audit_event_repository import AuditEventRepository


class AuditEventService:
    """Service for audit event operations."""

    def __init__(self, session: Session):
        self.session = session
        self.audit_repo = AuditEventRepository(session)

    def create_event(
        self,
        need_id: UUID | None,
        correlation_id: str,
        step_code: str,
        agent_code: str | None,
        tool_code: str | None,
        actor_type: str,
        actor_id: str | None,
        outcome: str,
        severity: str = "info",
        payload_ref: str | None = None,
    ) -> AuditEvent:
        """Create and persist an audit event."""
        event = AuditEvent(
            id=uuid.uuid4(),
            need_id=need_id,
            correlation_id=correlation_id,
            step_code=step_code,
            agent_code=agent_code,
            tool_code=tool_code,
            actor_type=actor_type,
            actor_id=actor_id,
            outcome=outcome,
            severity=severity,
            payload_ref=payload_ref,
        )
        return self.audit_repo.create(event)
