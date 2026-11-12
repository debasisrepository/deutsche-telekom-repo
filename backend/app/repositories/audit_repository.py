"""Audit Repository - Data access for audit logs and workflow events"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.workflow_event import WorkflowEvent


class AuditRepository:
    """Repository for audit logs and workflow events."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_workflow_events_for_case(self, case_id: int) -> list[WorkflowEvent]:
        """Get all workflow events for a case."""
        stmt = (
            select(WorkflowEvent)
            .where(WorkflowEvent.case_id == case_id)
            .order_by(WorkflowEvent.created_at.asc())
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_audit_logs_for_case(self, case_id: int) -> list[AuditLog]:
        """Get all audit logs for a case."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.case_id == case_id)
            .order_by(AuditLog.created_at.desc())
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())
