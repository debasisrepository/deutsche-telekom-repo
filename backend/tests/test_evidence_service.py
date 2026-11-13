import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models.supplier_evidence_item import SupplierEvidenceItem
from app.services.supplier_evidence_service import SupplierEvidenceService


def test_query_evidence_with_tol2_unavailable(db_session):
    """Test evidence query when TOL2 is unavailable, falls back to seed data."""
    service = SupplierEvidenceService(db_session)
    need_id = uuid.uuid4()

    seed_item = SupplierEvidenceItem(
        id=uuid.uuid4(),
        need_id=need_id,
        supplier_id="SUP-001",
        evidence_type="historical_sow",
        source_system="SEED",
        source_reference="SOW-2022-001",
        service_category="IT Services",
        business_unit_id=None,
        delivery_period=None,
        quality_rating=4.5,
        citation_text="Test SoW citation",
        is_seed_data=True,
        evidence_snapshot_timestamp=datetime.now(UTC),
        evidence_limited_flag=False,
    )
    db_session.add(seed_item)
    db_session.commit()

    result = service.query_evidence(
        need_id=str(need_id),
        service_type="Cloud Services",
    )

    assert result.evidence_limited_flag is True
    assert len(result.evidence_items) == 1
    assert result.evidence_items[0].supplier_id == "SUP-001"
    assert result.evidence_items[0].is_seed_data is True


def test_query_evidence_with_no_seed_data(db_session):
    """Test evidence query when TOL2 unavailable and no seed data exists."""
    service = SupplierEvidenceService(db_session)
    need_id = uuid.uuid4()

    result = service.query_evidence(
        need_id=str(need_id),
        service_type="Cloud Services",
    )

    assert result.evidence_limited_flag is True
    assert len(result.evidence_items) == 0


def test_query_evidence_multiple_suppliers(db_session):
    """Test evidence query returns multiple suppliers from seed data."""
    service = SupplierEvidenceService(db_session)
    need_id = uuid.uuid4()

    seed_items = [
        SupplierEvidenceItem(
            id=uuid.uuid4(),
            need_id=need_id,
            supplier_id=f"SUP-{i:03d}",
            evidence_type="historical_project",
            source_system="SEED",
            source_reference=f"PRJ-2023-{i:03d}",
            service_category="IT Services",
            business_unit_id=None,
            delivery_period=None,
            quality_rating=4.0 + (i * 0.1),
            citation_text=f"Project citation {i}",
            is_seed_data=True,
            evidence_snapshot_timestamp=datetime.now(UTC),
            evidence_limited_flag=False,
        )
        for i in range(1, 6)
    ]

    for item in seed_items:
        db_session.add(item)
    db_session.commit()

    result = service.query_evidence(
        need_id=str(need_id),
    )

    assert result.evidence_limited_flag is True
    assert len(result.evidence_items) == 5
    supplier_ids = [item.supplier_id for item in result.evidence_items]
    assert "SUP-001" in supplier_ids
    assert "SUP-005" in supplier_ids


def test_query_evidence_with_filters(db_session):
    """Test evidence query with various filters applied."""
    service = SupplierEvidenceService(db_session)
    need_id = uuid.uuid4()

    seed_item = SupplierEvidenceItem(
        id=uuid.uuid4(),
        need_id=need_id,
        supplier_id="SUP-CLOUD-001",
        evidence_type="historical_sow",
        source_system="SEED",
        source_reference="SOW-2022-001",
        service_category="Cloud Infrastructure",
        business_unit_id=None,
        delivery_period=None,
        quality_rating=4.5,
        citation_text="Cloud services SoW",
        is_seed_data=True,
        evidence_snapshot_timestamp=datetime.now(UTC),
        evidence_limited_flag=False,
    )
    db_session.add(seed_item)
    db_session.commit()

    result = service.query_evidence(
        need_id=str(need_id),
        service_type="Cloud Infrastructure",
        required_skills=["AWS", "Azure"],
        business_unit_id="BU-NORTH-001",
        panel_filters=["IT-CLOUD-PANEL-A"],
    )

    assert result.evidence_limited_flag is True
    assert len(result.evidence_items) == 1
