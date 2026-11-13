"""Need review service for ATS2."""
import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.models.need_attributes import NeedAttributes
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.need_attributes_repository import NeedAttributesRepository
from app.repositories.need_repository import NeedRepository
from app.schemas.review_schemas import AttributeReviewRequest, AttributeReviewResponse, NeedAttributesResponse


class NeedReviewService:
    """Service for ATS2 need attribute extraction review."""

    def __init__(self, session: Session):
        self.session = session
        self.need_repo = NeedRepository(session)
        self.attrs_repo = NeedAttributesRepository(session)
        self.audit_repo = AuditEventRepository(session)

    def review_attributes(
        self,
        need_id: UUID,
        request: AttributeReviewRequest,
        reviewer_id: str,
    ) -> AttributeReviewResponse:
        """
        ATS2: Capture reviewer decision on extracted attributes.

        Supports approve, modify, or reject actions. Persists reviewed state,
        logs decision, and advances workflow status.
        """
        # Retrieve need
        need = self.need_repo.get_by_id(need_id)
        if not need:
            raise ValueError(f"Need {need_id} not found")

        # Retrieve or create need_attributes
        attrs = self.attrs_repo.get_by_need_id(need_id)

        next_status = ""
        attrs_id = None

        if request.review_decision == "approve":
            # Approve existing extraction
            if not attrs:
                raise ValueError(f"No attributes found for need {need_id} to approve")
            attrs.review_status = "approved"
            attrs.reviewed_by = reviewer_id
            attrs.reviewed_at = datetime.now(UTC)
            self.attrs_repo.update(attrs)
            attrs_id = attrs.id

            # Advance to classification review
            need.status = "classification_review_pending"
            next_status = "classification_review_pending"

        elif request.review_decision == "modify":
            # Modify and approve
            if not request.need_attributes:
                raise ValueError("need_attributes required for modify decision")

            if attrs:
                # Update existing
                setattr(attrs, "service_type", request.need_attributes.service_type)
                setattr(attrs, "scope_description", request.need_attributes.scope_description)
                setattr(attrs, "estimated_volume_duration", request.need_attributes.estimated_volume_duration)
                setattr(attrs, "required_skills", request.need_attributes.required_skills)
                setattr(attrs, "budget_indication", request.need_attributes.budget_indication)
                setattr(attrs, "delivery_location", request.need_attributes.delivery_location)
                setattr(attrs, "field_confidence", request.need_attributes.field_confidence)
                attrs.schema_valid = True  # Reviewer validated
                attrs.review_status = "modified_approved"
                attrs.reviewed_by = reviewer_id
                attrs.reviewed_at = datetime.now(UTC)
                self.attrs_repo.update(attrs)
            else:
                # Create new
                attrs = NeedAttributes(
                    id=uuid.uuid4(),
                    need_id=need_id,
                    service_type=request.need_attributes.service_type,
                    scope_description=request.need_attributes.scope_description,
                    estimated_volume_duration=request.need_attributes.estimated_volume_duration,
                    required_skills=request.need_attributes.required_skills,
                    budget_indication=request.need_attributes.budget_indication,
                    delivery_location=request.need_attributes.delivery_location,
                    field_confidence=request.need_attributes.field_confidence,
                    schema_valid=True,
                    review_status="modified_approved",
                    reviewed_by=reviewer_id,
                    reviewed_at=datetime.now(UTC),
                )
                self.attrs_repo.create(attrs)

            attrs_id = attrs.id
            need.status = "classification_review_pending"
            next_status = "classification_review_pending"

        elif request.review_decision == "reject":
            # Reject extraction
            if attrs:
                attrs.review_status = "rejected"
                attrs.reviewed_by = reviewer_id
                attrs.reviewed_at = datetime.now(UTC)
                self.attrs_repo.update(attrs)
                attrs_id = attrs.id

            # Return to extraction remediation
            need.status = "extraction_review_pending"
            next_status = "extraction_review_pending"

        else:
            raise ValueError(f"Invalid review_decision: {request.review_decision}")

        # Update need
        self.need_repo.update(need)

        # Write audit event
        audit_event = AuditEvent(
            id=uuid.uuid4(),
            need_id=need_id,
            correlation_id=need.correlation_id,
            step_code="ATS2",
            agent_code="AGN1",
            tool_code=None,
            actor_type="human",
            actor_id=reviewer_id,
            outcome=request.review_decision,
            severity="info",
            payload_ref=f"decision={request.review_decision}, notes={request.reviewer_notes[:100] if request.reviewer_notes else 'none'}",
        )
        self.audit_repo.create(audit_event)

        # Commit transaction
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        # Build response with need_attributes if available
        need_attrs_response = None
        if attrs:
            need_attrs_response = NeedAttributesResponse.model_validate(attrs)
        
        return AttributeReviewResponse(
            need_id=need_id,
            review_decision=request.review_decision,
            next_workflow_status=next_status,
            need_attributes_id=attrs_id,
            need_attributes=need_attrs_response,
        )
