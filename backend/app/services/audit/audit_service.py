"""Audit Service - Immutable audit logging and workflow event recording"""
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.workflow_event import WorkflowEvent


class AuditService:
    """
    Service for recording immutable audit events and workflow state transitions.
    Ensures compliance with REQ-COMPLIANCE-001.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def record_workflow_event(
        self,
        case_id: int,
        event_type: str,
        from_state: str | None,
        to_state: str,
        actor_type: str,
        actor_id: str,
        payload: str
    ) -> WorkflowEvent:
        """
        Record a workflow state transition event.
        
        Args:
            case_id: Case ID
            event_type: Type of workflow event (e.g., 'case_created', 'state_transition')
            from_state: Previous workflow state (None for creation)
            to_state: New workflow state
            actor_type: Type of actor ('user', 'system', 'agent')
            actor_id: ID of actor (user ID or agent name)
            payload: Event-specific data
            
        Returns:
            Created WorkflowEvent
        """
        event = WorkflowEvent(
            case_id=case_id,
            event_type=event_type,
            from_state=from_state,
            to_state=to_state,
            actor_type=actor_type,
            actor_id=actor_id,
            payload=payload,
            requirement_tags="REQ-COMPLIANCE-001"
        )
        self.session.add(event)
        # Don't commit here - let caller control transaction
        return event
    
    def record_audit(
        self,
        case_id: int,
        action_type: str,
        actor_type: str,
        actor_id: str,
        target_type: str,
        target_id: str,
        audit_payload: str
    ) -> AuditLog:
        """
        Record an immutable audit log entry.
        
        Args:
            case_id: Case ID
            action_type: Type of action (e.g., 'case_creation', 'review_decision')
            actor_type: Type of actor ('user', 'system', 'agent')
            actor_id: ID of actor
            target_type: Type of target entity
            target_id: ID of target entity
            audit_payload: Audit-specific data
            
        Returns:
            Created AuditLog
        """
        log = AuditLog(
            case_id=case_id,
            action_type=action_type,
            actor_type=actor_type,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            audit_payload=audit_payload,
            requirement_tags="REQ-COMPLIANCE-001"
        )
        self.session.add(log)
        # Don't commit here - let caller control transaction
        return log
