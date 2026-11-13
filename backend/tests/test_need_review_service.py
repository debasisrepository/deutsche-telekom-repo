"""Unit tests for NeedReviewService."""
import pytest
import uuid
from datetime import UTC, datetime
from app.models.need import Need
from app.models.need_attributes import NeedAttributes
from app.services.need_review_service import NeedReviewService
from app.schemas.review_schemas import AttributeReviewRequest, NeedAttributesRequest


def test_review_approve(db_session):
    """Test approving extracted attributes."""
    # Create a need with attributes
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        status="extraction_review_pending",
        correlation_id="test-123",
    )
    db_session.add(need)
    
    attrs = NeedAttributes(
        id=uuid.uuid4(),
        need_id=need.id,
        service_type="IT Consulting",
        scope_description="Backend development",
        schema_valid=True,
    )
    db_session.add(attrs)
    db_session.commit()
    
    # Approve
    service = NeedReviewService(db_session)
    request = AttributeReviewRequest(review_decision="approve")
    
    response = service.review_attributes(need.id, request, "reviewer@example.com")
    
    assert response.review_decision == "approve"
    assert response.next_workflow_status == "classification_review_pending"
    
    # Check state changes
    db_session.refresh(need)
    db_session.refresh(attrs)
    assert need.status == "classification_review_pending"
    assert attrs.review_status == "approved"
    assert attrs.reviewed_by == "reviewer@example.com"


def test_review_modify(db_session):
    """Test modifying and approving attributes."""
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        status="extraction_review_pending",
        correlation_id="test-456",
    )
    db_session.add(need)
    db_session.commit()
    
    service = NeedReviewService(db_session)
    modified_attrs = NeedAttributesRequest(
        service_type="Cloud Migration",
        scope_description="AWS migration",
        estimated_volume_duration="6 months",
        required_skills='["AWS", "DevOps"]',
        budget_indication="$100k-$200k",
        delivery_location="Remote",
        field_confidence='{"service_type": 0.95}',
    )
    
    request = AttributeReviewRequest(
        review_decision="modify",
        need_attributes=modified_attrs,
        reviewer_notes="Updated service type",
    )
    
    response = service.review_attributes(need.id, request, "reviewer@example.com")
    
    assert response.review_decision == "modify"
    assert response.next_workflow_status == "classification_review_pending"
    
    # Check attributes were created/updated
    from app.repositories.need_attributes_repository import NeedAttributesRepository
    repo = NeedAttributesRepository(db_session)
    attrs = repo.get_by_need_id(need.id)
    
    assert attrs is not None
    assert attrs.service_type == "Cloud Migration"
    assert attrs.review_status == "modified_approved"


def test_review_reject(db_session):
    """Test rejecting extracted attributes."""
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-002",
        channel_type="supplier_offer",
        arrival_timestamp=datetime.now(UTC),
        status="extraction_review_pending",
        correlation_id="test-789",
    )
    db_session.add(need)
    
    attrs = NeedAttributes(
        id=uuid.uuid4(),
        need_id=need.id,
        service_type="Unknown",
        schema_valid=False,
    )
    db_session.add(attrs)
    db_session.commit()
    
    service = NeedReviewService(db_session)
    request = AttributeReviewRequest(
        review_decision="reject",
        reviewer_notes="Insufficient information",
    )
    
    response = service.review_attributes(need.id, request, "reviewer@example.com")
    
    assert response.review_decision == "reject"
    assert response.next_workflow_status == "extraction_review_pending"
    
    # Check state
    db_session.refresh(need)
    db_session.refresh(attrs)
    assert need.status == "extraction_review_pending"
    assert attrs.review_status == "rejected"


def test_review_creates_audit_event(db_session):
    """Test that review creates audit event."""
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        status="extraction_review_pending",
        correlation_id="test-audit",
    )
    db_session.add(need)
    
    attrs = NeedAttributes(
        id=uuid.uuid4(),
        need_id=need.id,
        service_type="Testing",
        schema_valid=True,
    )
    db_session.add(attrs)
    db_session.commit()
    
    service = NeedReviewService(db_session)
    request = AttributeReviewRequest(review_decision="approve")
    
    service.review_attributes(need.id, request, "audit-reviewer@example.com")
    
    # Check audit event
    from app.models.audit_event import AuditEvent
    audit = db_session.query(AuditEvent).filter(
        AuditEvent.need_id == need.id,
        AuditEvent.step_code == "ATS2",
    ).first()
    
    assert audit is not None
    assert audit.outcome == "approve"
    assert audit.actor_type == "human"
    assert audit.actor_id == "audit-reviewer@example.com"
