"""Need ingestion service for ATS1."""
import re
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.models.need import Need
from app.models.need_attributes import NeedAttributes
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.need_attributes_repository import NeedAttributesRepository
from app.repositories.need_repository import NeedRepository
from app.schemas.intake_schemas import NeedIntakeRequest, NeedIntakeResponse


class NeedIngestionService:
    """Service for ATS1 need ingestion and normalization."""

    def __init__(self, session: Session):
        self.session = session
        self.need_repo = NeedRepository(session)
        self.attrs_repo = NeedAttributesRepository(session)
        self.audit_repo = AuditEventRepository(session)

    def _mask_pii(self, text: str | None) -> str | None:
        """Mask PII (emails, phone numbers) in text."""
        if not text:
            return text

        # Mask emails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_MASKED]', text)
        # Mask phone numbers (basic pattern)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_MASKED]', text)
        text = re.sub(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE_MASKED]', text)

        return text

    def ingest_need(self, request: NeedIntakeRequest, correlation_id: str | None = None) -> NeedIntakeResponse:
        """
        ATS1: Ingest and normalize incoming need.

        Validates schema, masks PII, creates Need record, writes audit event.
        """
        # Generate correlation ID if not provided
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Validate channel_type (already done by Pydantic, but explicit check)
        valid_channels = {"rfp", "email", "phone", "supplier_offer"}
        if request.channel_type not in valid_channels:
            raise ValueError(f"Invalid channel_type. Must be one of: {valid_channels}")

        # Mask PII in normalized payload
        masked_payload = self._mask_pii(request.normalized_payload_json)

        # Create Need record
        need = Need(
            id=uuid.uuid4(),
            business_unit_id=request.business_unit_id,
            channel_type=request.channel_type,
            arrival_timestamp=datetime.now(UTC),
            raw_artifact_ref=request.raw_artifact_ref,
            normalized_payload_json=masked_payload,
            status="normalized",
            evidence_limited_flag=False,
            correlation_id=correlation_id,
        )

        try:
            # Persist need
            created_need = self.need_repo.create(need)

            # Create NeedAttributes if provided
            if request.need_attributes:
                attrs = NeedAttributes(
                    id=uuid.uuid4(),
                    need_id=created_need.id,
                    service_type=request.need_attributes.service_type,
                    scope_description=request.need_attributes.scope_description,
                    estimated_volume_duration=request.need_attributes.estimated_volume_duration,
                    required_skills=request.need_attributes.required_skills,
                    budget_indication=request.need_attributes.budget_indication,
                    delivery_location=request.need_attributes.delivery_location,
                    field_confidence=request.need_attributes.field_confidence,
                    schema_valid=True,
                    review_status="pending",
                )
                self.attrs_repo.create(attrs)

            # Write audit event
            audit_event = AuditEvent(
                id=uuid.uuid4(),
                need_id=created_need.id,
                correlation_id=correlation_id,
                step_code="ATS1",
                agent_code="AGN5",
                tool_code="TOL1",
                actor_type="system",
                actor_id="need_ingestion_service",
                outcome="success",
                severity="info",
                payload_ref=f"channel={request.channel_type}, business_unit={request.business_unit_id}",
            )
            self.audit_repo.create(audit_event)

            # Commit transaction
            self.session.commit()

            return NeedIntakeResponse(
                need_id=created_need.id,
                status=created_need.status,
                correlation_id=correlation_id,
            )

        except Exception as e:
            self.session.rollback()
            # Write audit event for failure
            audit_event = AuditEvent(
                id=uuid.uuid4(),
                need_id=None,
                correlation_id=correlation_id,
                step_code="ATS1",
                agent_code="AGN5",
                tool_code="TOL1",
                actor_type="system",
                actor_id="need_ingestion_service",
                outcome="error",
                severity="error",
                payload_ref=f"error={str(e)[:500]}",
            )
            self.audit_repo.create(audit_event)
            self.session.commit()
            raise
