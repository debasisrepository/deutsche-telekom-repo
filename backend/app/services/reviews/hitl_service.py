"""HITL Review Service - Human-in-the-loop review gate management"""
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.hitl_review import HITLReview
from app.models.need_case import NeedCase
from app.services.audit.audit_service import AuditService


class HITLService:
    """
    Manages human-in-the-loop review gates for AMBER steps.
    
    Supports:
    - Opening review tasks (extraction, classification)
    - Applying reviewer decisions (approve, edit, reject, override)
    - Preserving generated-versus-final payload distinction
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.audit_service = AuditService(session)
    
    def open_review(
        self,
        case_id: int,
        review_type: str,
        generated_payload: dict[str, Any],
        assigned_role: str = "reviewer"
    ) -> HITLReview:
        """
        Open a new HITL review task.
        
        Args:
            case_id: Case identifier
            review_type: Type of review (extraction, classification)
            generated_payload: AI-generated output to be reviewed
            assigned_role: Role authorized to review
            
        Returns:
            Created HITLReview record in pending status
        """
        review = HITLReview(
            case_id=case_id,
            review_type=review_type,
            status="pending",
            assigned_role=assigned_role,
            generated_payload=json.dumps(generated_payload)
        )
        
        self.session.add(review)
        self.session.flush()
        
        # Record audit event
        self.audit_service.record_workflow_event(
            case_id=case_id,
            event_type=f"{review_type}_review_opened",
            from_state=None,
            to_state=f"{review_type}_pending_review",
            actor_type="system",
            actor_id="AGN1",
            payload=json.dumps({"review_id": review.id, "review_type": review_type})
        )
        
        return review
    
    def apply_decision(
        self,
        review_id: int,
        decision: str,
        reviewer_id: int,
        edited_payload: dict[str, Any] | None = None
    ) -> HITLReview:
        """
        Apply reviewer decision to pending review.
        
        Args:
            review_id: Review record identifier
            decision: Decision type (approve, edit, reject, override)
            reviewer_id: ID of user making decision
            edited_payload: Optional edited payload (required for 'edit' and 'override' decisions)
            
        Returns:
            Updated HITLReview record with decision applied
            
        Raises:
            ValueError: If review not found or not in pending status
        """
        review = self.session.get(HITLReview, review_id)
        
        if review is None:
            raise ValueError(f"Review {review_id} not found")
        
        if review.status != "pending":
            raise ValueError(f"Review {review_id} is not pending (status: {review.status})")
        
        # Validate decision
        valid_decisions = ["approve", "edit", "reject", "override"]
        if decision not in valid_decisions:
            raise ValueError(f"Invalid decision: {decision}. Must be one of {valid_decisions}")
        
        # Apply decision
        review.decision = decision
        review.reviewer_id = reviewer_id
        review.reviewed_at = datetime.now(UTC)
        
        if decision == "approve":
            # Approve as-is: final payload = generated payload
            review.final_payload = review.generated_payload
            review.status = "approved"
        
        elif decision == "edit":
            # Approve with edits: final payload = edited payload
            if edited_payload is None:
                raise ValueError("Edited payload required for 'edit' decision")
            review.final_payload = json.dumps(edited_payload)
            review.status = "approved"
        
        elif decision == "reject":
            # Reject: no final payload, requires rework
            review.status = "rejected"
        
        elif decision == "override":
            # Override (for classification): final payload = overridden verdict
            if edited_payload is None:
                raise ValueError("Override payload required for 'override' decision")
            review.final_payload = json.dumps(edited_payload)
            review.status = "approved"
        
        self.session.flush()
        
        # Record audit event
        self.audit_service.record_workflow_event(
            case_id=review.case_id,
            event_type=f"{review.review_type}_review_{decision}",
            from_state=f"{review.review_type}_pending_review",
            to_state=f"{review.review_type}_{review.status}",
            actor_type="user",
            actor_id=str(reviewer_id),
            payload=json.dumps({
                "review_id": review.id,
                "decision": decision,
                "review_type": review.review_type
            })
        )
        
        self.audit_service.record_audit(
            case_id=review.case_id,
            action_type=f"hitl_review_{decision}",
            actor_type="user",
            actor_id=str(reviewer_id),
            target_type="hitl_review",
            target_id=str(review.id),
            audit_payload=json.dumps({
                "review_type": review.review_type,
                "decision": decision,
                "has_edits": edited_payload is not None
            })
        )
        
        # Update case workflow state if review approved
        if review.status == "approved":
            self._advance_case_workflow(review)
        
        return review
    
    def _advance_case_workflow(self, review: HITLReview) -> None:
        """
        Advance case workflow state after review approval.
        
        Args:
            review: Approved HITLReview record
        """
        case = self.session.get(NeedCase, review.case_id)
        if case is None:
            return
        
        # Determine next workflow state based on review type
        if review.review_type == "extraction":
            case.workflow_state = "extraction_approved"
            case.next_action = "classification_pending"
        
        elif review.review_type == "classification":
            # Classification approved - check verdict for routing
            final_payload = json.loads(review.final_payload) if review.final_payload else {}
            verdict = final_payload.get("confirmed_verdict") or final_payload.get("ai_verdict")
            
            if verdict == "single_resource":
                case.workflow_state = "classification_approved"
                case.next_action = "vms_handoff_pending"
            else:
                case.workflow_state = "classification_approved"
                case.next_action = "evidence_retrieval_pending"
        
        self.session.flush()
