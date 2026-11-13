"""AuditEvent repository for data access."""
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


class AuditEventRepository:
    """Repository for AuditEvent CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, event: AuditEvent) -> AuditEvent:
        """Create a new audit event record."""
        self.session.add(event)
        self.session.flush()
        self.session.refresh(event)
        return event
