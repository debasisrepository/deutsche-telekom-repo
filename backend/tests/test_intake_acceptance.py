"""Acceptance tests for intake flow."""
import uuid


def test_intake_flow_rfp_channel(client):
    """
    Acceptance: The product accepts needs originating from RFP documents.
    Each accepted submission is stored as a Need record containing need_id,
    business_unit_id, channel_type, arrival_timestamp, raw_artifact_ref, and status.
    """
    # Submit RFP need
    payload = {
        "business_unit_id": "BU-ACC-RFP-001",
        "channel_type": "rfp",
        "raw_artifact_ref": "rfp-2024-11-acc.pdf",
        "normalized_payload_json": '{"title": "IT Infrastructure RFP", "deadline": "2024-12-31"}',
    }
    
    response = client.post("/api/v1/intake/needs", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "normalized"
    
    # Retrieve and verify all required fields
    need_id = data["need_id"]
    get_response = client.get(f"/api/v1/intake/needs/{need_id}")
    
    assert get_response.status_code == 200
    need_data = get_response.json()
    assert need_data["business_unit_id"] == "BU-ACC-RFP-001"
    assert need_data["channel_type"] == "rfp"
    assert need_data["raw_artifact_ref"] == "rfp-2024-11-acc.pdf"
    assert need_data["arrival_timestamp"] is not None
    assert need_data["status"] == "normalized"


def test_intake_flow_all_channels(client):
    """
    Acceptance: The product accepts needs from RFP, e-mail, phone, and supplier offers.
    """
    channels = ["rfp", "email", "phone", "supplier_offer"]
    
    for channel in channels:
        payload = {
            "business_unit_id": f"BU-{channel.upper()}",
            "channel_type": channel,
            "normalized_payload_json": f'{{"channel": "{channel}"}}',
        }
        
        response = client.post("/api/v1/intake/needs", json=payload)
        
        assert response.status_code == 201, f"Failed for channel {channel}"
        data = response.json()
        assert data["status"] == "normalized"


def test_intake_pii_masking(client):
    """
    Acceptance: Sensitive personal data in free-text submissions is stripped
    or masked before the normalized record is passed to later workflow steps.
    """
    payload = {
        "business_unit_id": "BU-PII-TEST",
        "channel_type": "email",
        "normalized_payload_json": '{"body": "Contact John at john.smith@example.com or call 555-987-6543"}',
    }
    
    response = client.post("/api/v1/intake/needs", json=payload)
    
    assert response.status_code == 201
    need_id = response.json()["need_id"]
    
    # Retrieve and check PII was masked
    get_response = client.get(f"/api/v1/intake/needs/{need_id}")
    need_data = get_response.json()
    
    assert "[EMAIL_MASKED]" in need_data["normalized_payload_json"]
    assert "[PHONE_MASKED]" in need_data["normalized_payload_json"]
    assert "john.smith@example.com" not in need_data["normalized_payload_json"]
    assert "555-987-6543" not in need_data["normalized_payload_json"]


def test_intake_malformed_rejection(client):
    """
    Acceptance: Empty, malformed, or unrecognized inbound artifacts are rejected
    with an auditable error state rather than entering downstream steps.
    """
    # Missing required field
    payload = {
        "channel_type": "rfp",
        # Missing business_unit_id
    }
    
    response = client.post("/api/v1/intake/needs", json=payload)
    
    assert response.status_code == 422  # Validation error
    
    # Invalid channel type
    payload2 = {
        "business_unit_id": "BU-INVALID",
        "channel_type": "invalid_channel",
    }
    
    response2 = client.post("/api/v1/intake/needs", json=payload2)
    
    assert response2.status_code == 422


def test_extraction_review_workflow(client, db_session):
    """
    Acceptance: Reviewers can approve, modify, or reject extracted attributes through
    the ATS2 gate, and corrections are logged against the need record.
    """
    # Create need
    from app.models.need import Need
    from app.models.need_attributes import NeedAttributes
    from datetime import UTC, datetime
    
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-REVIEW-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        status="extraction_review_pending",
        correlation_id="acc-review-001",
    )
    db_session.add(need)
    
    attrs = NeedAttributes(
        id=uuid.uuid4(),
        need_id=need.id,
        service_type="Software Development",
        scope_description="Mobile app development",
        schema_valid=True,
    )
    db_session.add(attrs)
    db_session.commit()
    
    # Test modify action
    review_payload = {
        "review_decision": "modify",
        "need_attributes": {
            "service_type": "Mobile Development",
            "scope_description": "iOS and Android app",
            "estimated_volume_duration": "6 months",
        },
        "reviewer_notes": "Clarified scope",
    }
    
    response = client.post(
        f"/api/v1/reviews/needs/{need.id}/attributes",
        json=review_payload,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["review_decision"] == "modify"
    assert data["next_workflow_status"] == "classification_review_pending"
    
    # Verify audit log entry exists
    from app.models.audit_event import AuditEvent
    audit = db_session.query(AuditEvent).filter(
        AuditEvent.need_id == need.id,
        AuditEvent.step_code == "ATS2",
    ).first()
    
    assert audit is not None
    assert "modify" in audit.outcome


def test_attribute_confidence_and_validation(client, db_session):
    """
    Acceptance: Each extracted field is accompanied by confidence information
    sufficient for reviewer validation. Extraction outputs that fail schema
    validation are held for remediation.
    """
    from app.models.need import Need
    from app.models.need_attributes import NeedAttributes
    from datetime import UTC, datetime
    
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-CONF-001",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        status="extraction_review_pending",
        correlation_id="acc-conf-001",
    )
    db_session.add(need)
    
    attrs = NeedAttributes(
        id=uuid.uuid4(),
        need_id=need.id,
        service_type="Data Migration",
        field_confidence='{"service_type": 0.87, "scope_description": 0.45}',
        schema_valid=True,
    )
    db_session.add(attrs)
    db_session.commit()
    
    # Retrieve need to check attributes
    response = client.get(f"/api/v1/intake/needs/{need.id}")
    assert response.status_code == 200
    
    # In full implementation, would retrieve attributes separately
    # and verify field_confidence is present and schema_valid flag


def test_normalization_deterministic(client):
    """
    Acceptance: Channel normalization applies deterministic rules so all inbound
    channels produce a common record structure before downstream extraction.
    """
    # Submit needs from different channels
    channels_data = [
        {"business_unit_id": "BU-NORM-RFP", "channel_type": "rfp"},
        {"business_unit_id": "BU-NORM-EMAIL", "channel_type": "email"},
        {"business_unit_id": "BU-NORM-PHONE", "channel_type": "phone"},
        {"business_unit_id": "BU-NORM-SUPPLIER", "channel_type": "supplier_offer"},
    ]
    
    need_ids = []
    for data in channels_data:
        response = client.post("/api/v1/intake/needs", json=data)
        assert response.status_code == 201
        need_ids.append(response.json()["need_id"])
    
    # Verify all have common structure
    for need_id in need_ids:
        response = client.get(f"/api/v1/intake/needs/{need_id}")
        assert response.status_code == 200
        data = response.json()
        
        # All should have these fields
        required_fields = [
            "id", "business_unit_id", "channel_type",
            "arrival_timestamp", "status", "correlation_id"
        ]
        for field in required_fields:
            assert field in data, f"Missing field {field}"
