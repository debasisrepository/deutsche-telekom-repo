"""Integration tests for panel mapping and niche research API endpoints."""

import uuid
from datetime import UTC, datetime

from app.models.need import Need


def test_panel_mappings_endpoint_success(client, db_session):
    """Test POST /api/v1/panel-mappings success."""
    # Create a test need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-001.pdf",
        normalized_payload_json='{"service": "cloud hosting"}',
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.95,
        correlation_id="test-int-001",
    )
    db_session.add(need)
    db_session.commit()

    # Call panel mappings endpoint
    response = client.post(
        "/api/v1/panel-mappings",
        json={
            "need_id": str(need.id),
            "need_category": "cloud_hosting",
        },
        headers={"X-Correlation-Id": "test-int-001"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["need_id"] == str(need.id)
    assert data["correlation_id"] == "test-int-001"
    assert "candidate_suppliers" in data
    assert isinstance(data["candidate_suppliers"], list)
    assert "coverage_gap_flag" in data
    assert isinstance(data["coverage_gap_flag"], bool)


def test_panel_mappings_endpoint_not_found(client):
    """Test POST /api/v1/panel-mappings with non-existent need."""
    response = client.post(
        "/api/v1/panel-mappings",
        json={
            "need_id": str(uuid.uuid4()),
            "need_category": "cloud_hosting",
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_niche_research_endpoint_success(client, db_session):
    """Test POST /api/v1/niche-research success."""
    # Create a test need classified as it_service
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-002",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-002.pdf",
        normalized_payload_json='{"service": "specialized hosting"}',
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.87,
        correlation_id="test-int-002",
    )
    db_session.add(need)
    db_session.commit()

    # Call niche research endpoint
    response = client.post(
        "/api/v1/niche-research",
        json={
            "need_id": str(need.id),
            "capability_gap": "Quantum-resistant encryption",
            "approved_source_list": ["Gaia-X participant registry", "BSI C5 attestation"],
        },
        headers={"X-Correlation-Id": "test-int-002"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["need_id"] == str(need.id)
    assert data["correlation_id"] == "test-int-002"
    assert "niche_research_dossier" in data
    assert isinstance(data["niche_research_dossier"], list)
    assert data["review_required"] is True


def test_niche_research_endpoint_not_found(client):
    """Test POST /api/v1/niche-research with non-existent need."""
    response = client.post(
        "/api/v1/niche-research",
        json={
            "need_id": str(uuid.uuid4()),
            "capability_gap": "Some gap",
            "approved_source_list": ["Gaia-X"],
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_niche_research_endpoint_wrong_classification(client, db_session):
    """Test POST /api/v1/niche-research with single_resource need."""
    # Create a need classified as single_resource
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-003",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-003.pdf",
        normalized_payload_json='{"service": "contractor"}',
        status="classified_single_resource",
        classification_verdict="single_resource",
        classification_confidence=0.95,
        correlation_id="test-int-003",
    )
    db_session.add(need)
    db_session.commit()

    response = client.post(
        "/api/v1/niche-research",
        json={
            "need_id": str(need.id),
            "capability_gap": "Some gap",
            "approved_source_list": ["Gaia-X"],
        },
    )

    assert response.status_code == 400
    assert "it_service" in response.json()["detail"]


def test_niche_research_endpoint_no_approved_sources(client, db_session):
    """Test POST /api/v1/niche-research without approved sources."""
    # Create a test need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-004",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="rfp-2024-004.pdf",
        normalized_payload_json='{"service": "specialized hosting"}',
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.87,
        correlation_id="test-int-004",
    )
    db_session.add(need)
    db_session.commit()

    response = client.post(
        "/api/v1/niche-research",
        json={
            "need_id": str(need.id),
            "capability_gap": "Some gap",
            "approved_source_list": [],
        },
    )

    assert response.status_code == 400
    assert "approved_source_list" in response.json()["detail"]
