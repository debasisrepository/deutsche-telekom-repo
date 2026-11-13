"""Classification decision service for ATS3."""
import json
import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.models.classification_review import ClassificationReview
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.classification_review_repository import ClassificationReviewRepository
from app.repositories.need_repository import NeedRepository
from app.schemas.vms_schemas import ClassificationReviewRequest, ClassificationReviewResponse


class ClassificationDecisionService:
    """Service for ATS3 classification review and decision capture."""

    # Classification confidence threshold - below this triggers escalation
    LOW_CONFIDENCE_THRESHOLD = 0.70

    def __init__(self, session: Session):
        self.session = session
        self.need_repo = NeedRepository(session)
        self.review_repo = ClassificationReviewRepository(session)
        self.audit_repo = AuditEventRepository(session)

    def review_classification(
        self,
        need_id: UUID,
        request: ClassificationReviewRequest,
        reviewer_id: str,
    ) -> ClassificationReviewResponse:
        """
        ATS3: Capture reviewer decision on classification.

        Enforces allowed verdicts (single_resource | it_service),
        logs decision with rationale and exemplars, advances workflow.
        Low-confidence cases held for review, never auto-routed.
        """
        # Retrieve need
        need = self.need_repo.get_by_id(need_id)
        if not need:
            raise ValueError(f"Need {need_id} not found")

        # Enforce allowed verdicts
        allowed_verdicts = ["single_resource", "it_service"]
        if request.classification_verdict not in allowed_verdicts:
            raise ValueError(
                f"Invalid classification_verdict: {request.classification_verdict}. "
                f"Allowed values: {', '.join(allowed_verdicts)}"
            )

        # Determine if escalation required based on confidence threshold
        escalation_required = request.escalation_required
        if request.classification_confidence < self.LOW_CONFIDENCE_THRESHOLD:
            escalation_required = True

        # Determine next workflow status based on review decision
        next_status = ""
        if request.review_decision == "approve":
            if request.classification_verdict == "single_resource":
                next_status = "classified_single_resource"
            elif request.classification_verdict == "it_service":
                next_status = "classified_it_service"
        elif request.review_decision == "modify":
            # Modified classification still advances
            if request.classification_verdict == "single_resource":
                next_status = "classified_single_resource"
            elif request.classification_verdict == "it_service":
                next_status = "classified_it_service"
        elif request.review_decision == "reject":
            # Rejected classification returns to review pending
            next_status = "classification_review_pending"
        else:
            raise ValueError(f"Invalid review_decision: {request.review_decision}")

        # If escalation required, hold in review pending regardless
        if escalation_required and request.review_decision in ["approve", "modify"]:
            next_status = "classification_review_pending"

        # Convert exemplars list to JSON string for storage
        exemplars_json = json.dumps(request.exemplars_referenced) if request.exemplars_referenced else None

        # Create classification review record
        review = ClassificationReview(
            id=uuid.uuid4(),
            need_id=need_id,
            classification_verdict=request.classification_verdict,
            classification_confidence=request.classification_confidence,
            rationale=request.rationale,
            review_decision=request.review_decision,
            reviewer_id=reviewer_id,
            escalation_required=escalation_required,
            exemplars_referenced=exemplars_json,
        )
        self.review_repo.create(review)

        # Update need with classification verdict and workflow status
        need.classification_verdict = request.classification_verdict
        need.classification_confidence = request.classification_confidence
        need.status = next_status
        self.need_repo.update(need)

        # Write audit event
        audit_event = AuditEvent(
            id=uuid.uuid4(),
            need_id=need_id,
            correlation_id=need.correlation_id,
            step_code="ATS3",
            agent_code="AGN1",
            tool_code=None,
            actor_type="human",
            actor_id=reviewer_id,
            outcome=request.review_decision,
            severity="warning" if escalation_required else "info",
            payload_ref=(
                f"verdict={request.classification_verdict}, "
                f"confidence={request.classification_confidence:.4f}, "
                f"escalation={escalation_required}"
            ),
        )
        self.audit_repo.create(audit_event)

        # Commit transaction
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return ClassificationReviewResponse(
            classification_review_id=review.id,
            need_id=need_id,
            review_decision=request.review_decision,
            classification_verdict=request.classification_verdict,
            classification_confidence=request.classification_confidence,
            rationale=request.rationale,
            exemplars_referenced=request.exemplars_referenced,
            escalation_required=escalation_required,
            next_workflow_status=next_status,
            reviewed_by=reviewer_id,
            reviewed_at=datetime.now(UTC),
        )
