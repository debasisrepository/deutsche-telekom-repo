"""Integration tests for review API."""
import uuid
from datetime import UTC, datetime


def test_review_attributes_approve(client, db_session):
    """Test POST /api/v1/reviews/needs/{need_id}/attributes - approve."""
    # Create need with attributes
    from app.models.need import Need
    from app.models.need_attributes import NeedAttributes
    
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-REV-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        status="extraction_review_pending",
        correlation_id="review-test-001",
    )
    db_session.add(need)
    
    attrs = NeedAttributes(
        id=uuid.uuid4(),
        need_id=need.id,
        service_type="Cloud Services",
        scope_description="AWS deployment",
        schema_valid=True,
    )
    db_session.add(attrs)
    db_session.commit()
    
    # Approve
    payload = {"review_decision": "approve"}
    response = client.post(f"/api/v1/reviews/needs/{need.id}/attributes", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["review_decision"] == "approve"
    assert data["next_workflow_status"] == "classification_review_pending"


def test_review_attributes_modify(client, db_session):
    """Test POST /api/v1/reviews/needs/{need_id}/attributes - modify."""
    from app.models.need import Need
    
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-REV-002",
        channel_type="email",
        arrival_timestamp=datetime.now(UTC),
        status="extraction_review_pending",
        correlation_id="review-test-002",
    )
    db_session.add(need)
    db_session.commit()
    
    # Modify with new attributes
    payload = {
        "review_decision": "modify",
        "need_attributes": {
            "service_type": "Data Analytics",
            "scope_description": "ETL pipeline development",
            "estimated_volume_duration": "3 months",
            "required_skills": '["Python", "SQL"]',
        },
        "reviewer_notes": "Corrected service type",
    }
    
    response = client.post(f"/api/v1/reviews/needs/{need.id}/attributes", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["review_decision"] == "modify"
    assert data["need_attributes_id"] is not None


def test_review_attributes_reject(client, db_session):
    """Test POST /api/v1/reviews/needs/{need_id}/attributes - reject."""
    from app.models.need import Need
    from app.models.need_attributes import NeedAttributes
    
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-REV-003",
        channel_type="phone",
        arrival_timestamp=datetime.now(UTC),
        status="extraction_review_pending",
        correlation_id="review-test-003",
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
    
    # Reject
    payload = {
        "review_decision": "reject",
        "reviewer_notes": "Incomplete extraction",
    }
    
    response = client.post(f"/api/v1/reviews/needs/{need.id}/attributes", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["review_decision"] == "reject"
    assert data["next_workflow_status"] == "extraction_review_pending"


def test_review_attributes_not_found(client):
    """Test review returns 400 for non-existent need."""
    fake_id = uuid.uuid4()
    payload = {"review_decision": "approve"}
    
    response = client.post(f"/api/v1/reviews/needs/{fake_id}/attributes", json=payload)
    
    assert response.status_code == 400
