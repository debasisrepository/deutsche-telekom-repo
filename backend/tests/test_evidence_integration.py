import json
import uuid
from datetime import UTC, datetime

import pytest

from app.models.supplier_evidence_item import SupplierEvidenceItem


def test_evidence_query_endpoint_with_seed_data(client, db_session):
    """Test POST /api/v1/evidence/queries returns seed data when TOL2 unavailable."""
    need_id = uuid.uuid4()

    seed_item = SupplierEvidenceItem(
        id=uuid.uuid4(),
        need_id=need_id,
        supplier_id="SUP-TEST-001",
        evidence_type="historical_sow",
        source_system="SEED",
        source_reference="SOW-2022-TEST",
        service_category="IT Services",
        business_unit_id=None,
        delivery_period=None,
        quality_rating=4.3,
        citation_text="Test evidence citation",
        is_seed_data=True,
        evidence_snapshot_timestamp=datetime.now(UTC),
        evidence_limited_flag=False,
    )
    db_session.add(seed_item)
    db_session.commit()

    response = client.post(
        "/api/v1/evidence/queries",
        json={
            "need_id": str(need_id),
            "service_type": "Cloud Services",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["evidence_limited_flag"] is True
    assert len(data["evidence_items"]) == 1
    assert data["evidence_items"][0]["supplier_id"] == "SUP-TEST-001"
    assert data["evidence_items"][0]["is_seed_data"] is True


def test_evidence_query_endpoint_with_no_data(client, db_session):
    """Test POST /api/v1/evidence/queries returns empty list when no seed data."""
    need_id = uuid.uuid4()

    response = client.post(
        "/api/v1/evidence/queries",
        json={
            "need_id": str(need_id),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["evidence_limited_flag"] is True
    assert len(data["evidence_items"]) == 0


def test_evidence_query_endpoint_with_correlation_id(client, db_session):
    """Test evidence query endpoint includes correlation ID in response."""
    need_id = uuid.uuid4()
    correlation_id = "CORR-TEST-001"

    response = client.post(
        "/api/v1/evidence/queries",
        json={
            "need_id": str(need_id),
        },
        headers={"X-Correlation-Id": correlation_id},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["correlation_id"] == correlation_id


def test_evidence_query_endpoint_with_filters(client, db_session):
    """Test evidence query endpoint accepts all filter parameters."""
    need_id = uuid.uuid4()

    response = client.post(
        "/api/v1/evidence/queries",
        json={
            "need_id": str(need_id),
            "service_type": "Cloud Infrastructure",
            "required_skills": ["AWS", "Azure", "Kubernetes"],
            "business_unit_id": "BU-NORTH-001",
            "panel_filters": ["IT-CLOUD-PANEL-A", "IT-INFRA-PANEL-B"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "evidence_items" in data
    assert "evidence_limited_flag" in data
    assert "evidence_snapshot_timestamp" in data


def test_evidence_query_endpoint_multiple_suppliers(client, db_session):
    """Test evidence query returns multiple supplier evidence items."""
    need_id = uuid.uuid4()

    for i in range(1, 6):
        seed_item = SupplierEvidenceItem(
            id=uuid.uuid4(),
            need_id=need_id,
            supplier_id=f"SUP-{i:03d}",
            evidence_type="historical_project",
            source_system="SEED",
            source_reference=f"PRJ-2023-{i:03d}",
            service_category="IT Services",
            business_unit_id=None,
            delivery_period=None,
            quality_rating=4.0,
            citation_text=f"Project citation {i}",
            is_seed_data=True,
            evidence_snapshot_timestamp=datetime.now(UTC),
            evidence_limited_flag=False,
        )
        db_session.add(seed_item)
    db_session.commit()

    response = client.post(
        "/api/v1/evidence/queries",
        json={
            "need_id": str(need_id),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["evidence_items"]) == 5


def test_evidence_query_validates_required_fields(client):
    """Test evidence query endpoint requires need_id."""
    response = client.post(
        "/api/v1/evidence/queries",
        json={
            "service_type": "Cloud Services",
        },
    )

    assert response.status_code == 422


def test_validation_endpoint_pass_with_4_suppliers(client):
    """Test POST /api/v1/longlists/{id}/validate-count passes with 4 suppliers."""
    proposal_id = str(uuid.uuid4())

    response = client.post(
        f"/api/v1/longlists/{proposal_id}/validate-count",
        json={
            "proposal_or_longlist_id": proposal_id,
            "supplier_ids": ["SUP-001", "SUP-002", "SUP-003", "SUP-004"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["validation_verdict"] == "pass"
    assert data["supplier_count"] == 4
    assert len(data["violations"]) == 0


def test_validation_endpoint_fail_with_2_suppliers(client):
    """Test validation endpoint fails with 2 suppliers."""
    proposal_id = str(uuid.uuid4())

    response = client.post(
        f"/api/v1/longlists/{proposal_id}/validate-count",
        json={
            "proposal_or_longlist_id": proposal_id,
            "supplier_ids": ["SUP-001", "SUP-002"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["validation_verdict"] == "fail"
    assert data["supplier_count"] == 2
    assert len(data["violations"]) == 1


def test_validation_endpoint_fail_with_7_suppliers(client):
    """Test validation endpoint fails with 7 suppliers."""
    proposal_id = str(uuid.uuid4())

    response = client.post(
        f"/api/v1/longlists/{proposal_id}/validate-count",
        json={
            "proposal_or_longlist_id": proposal_id,
            "supplier_ids": [f"SUP-{i:03d}" for i in range(1, 8)],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["validation_verdict"] == "fail"
    assert data["supplier_count"] == 7
    assert len(data["violations"]) == 1
