"""Unit tests for NeedIngestionService."""
import pytest
from app.services.need_ingestion_service import NeedIngestionService
from app.schemas.intake_schemas import NeedIntakeRequest


def test_ingest_need_success(db_session):
    """Test successful need ingestion."""
    service = NeedIngestionService(db_session)
    
    request = NeedIntakeRequest(
        business_unit_id="BU-001",
        channel_type="rfp",
        raw_artifact_ref="rfp-2024-001.pdf",
        normalized_payload_json='{"title": "IT Services RFP"}',
    )
    
    response = service.ingest_need(request, "test-correlation-123")
    
    assert response.need_id is not None
    assert response.status == "normalized"
    assert response.correlation_id == "test-correlation-123"


def test_ingest_need_masks_pii(db_session):
    """Test that PII is masked in normalized payload."""
    service = NeedIngestionService(db_session)
    
    request = NeedIntakeRequest(
        business_unit_id="BU-001",
        channel_type="email",
        normalized_payload_json='{"contact": "john.doe@example.com", "phone": "555-123-4567"}',
    )
    
    response = service.ingest_need(request)
    
    # Verify need was created
    from app.repositories.need_repository import NeedRepository
    repo = NeedRepository(db_session)
    need = repo.get_by_id(response.need_id)
    
    # Check that PII was masked
    assert "[EMAIL_MASKED]" in need.normalized_payload_json
    assert "[PHONE_MASKED]" in need.normalized_payload_json
    assert "john.doe@example.com" not in need.normalized_payload_json


def test_ingest_need_invalid_channel(db_session):
    """Test that invalid channel types are rejected."""
    service = NeedIngestionService(db_session)
    
    # This should fail Pydantic validation before reaching service
    with pytest.raises(Exception):
        request = NeedIntakeRequest(
            business_unit_id="BU-001",
            channel_type="invalid_channel",
        )


def test_ingest_need_creates_audit_event(db_session):
    """Test that audit event is created on ingestion."""
    service = NeedIngestionService(db_session)
    
    request = NeedIntakeRequest(
        business_unit_id="BU-001",
        channel_type="phone",
        normalized_payload_json='{"notes": "Customer request"}',
    )
    
    response = service.ingest_need(request)
    
    # Verify audit event was created
    from app.models.audit_event import AuditEvent
    audit = db_session.query(AuditEvent).filter(
        AuditEvent.need_id == response.need_id,
        AuditEvent.step_code == "ATS1",
    ).first()
    
    assert audit is not None
    assert audit.outcome == "success"
    assert audit.agent_code == "AGN5"
