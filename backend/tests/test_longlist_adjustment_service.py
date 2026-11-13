"""Unit tests for LonglistAdjustmentService (ATS10)."""

import json
import uuid
from datetime import datetime

import pytest

from app.models.longlist import Longlist
from app.models.need import Need
from app.services.longlist_adjustment_service import LonglistAdjustmentService


def test_capture_adjustment_add_supplier(db_session):
    """Test capturing an add adjustment."""
    # Create need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=pytest.now,
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.95,
        evidence_limited_flag=False,
        correlation_id="test-correlation-1",
    )
    db_session.add(need)
    db_session.commit()

    # Create longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        proposal_id=uuid.uuid4(),
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Capture adjustment
    service = LonglistAdjustmentService(db_session)
    timestamp = datetime.utcnow()
    response = service.capture_adjustment(
        longlist_id=longlist.id,
        supplier_id="SUP-0045",
        action="add",
        reason="BU requested additional supplier for diversity",
        actor="bu.cloudops.lead",
        timestamp=timestamp,
        correlation_id="test-correlation-1",
    )

    # Assertions
    assert response.adjustment_id is not None
    assert response.longlist_id == longlist.id
    assert "SUP-0045" in response.updated_suppliers
    assert len(response.updated_suppliers) == 4
    assert response.validation_verdict == "pass"  # 4 suppliers within 3-6 range
    assert response.change_history_count == 1


def test_capture_adjustment_remove_supplier(db_session):
    """Test capturing a remove adjustment."""
    # Create need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-002",
        channel_type="email",
        arrival_timestamp=pytest.now,
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.92,
        evidence_limited_flag=False,
        correlation_id="test-correlation-2",
    )
    db_session.add(need)
    db_session.commit()

    # Create longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        proposal_id=uuid.uuid4(),
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Capture adjustment
    service = LonglistAdjustmentService(db_session)
    timestamp = datetime.utcnow()
    response = service.capture_adjustment(
        longlist_id=longlist.id,
        supplier_id="SUP-0045",
        action="remove",
        reason="Supplier declined to participate",
        actor="procurement.analyst",
        timestamp=timestamp,
        correlation_id="test-correlation-2",
    )

    # Assertions
    assert response.adjustment_id is not None
    assert "SUP-0045" not in response.updated_suppliers
    assert len(response.updated_suppliers) == 3
    assert response.validation_verdict == "pass"  # 3 suppliers at minimum
    assert response.change_history_count == 1


def test_capture_adjustment_validation_fails(db_session):
    """Test that validation reruns and can fail after adjustment."""
    # Create need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-003",
        channel_type="rfp",
        arrival_timestamp=pytest.now,
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.88,
        evidence_limited_flag=False,
        correlation_id="test-correlation-3",
    )
    db_session.add(need)
    db_session.commit()

    # Create longlist with minimum suppliers
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        proposal_id=uuid.uuid4(),
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Remove supplier causing count to drop below minimum
    service = LonglistAdjustmentService(db_session)
    timestamp = datetime.utcnow()
    response = service.capture_adjustment(
        longlist_id=longlist.id,
        supplier_id="SUP-0307",
        action="remove",
        reason="Testing validation failure",
        actor="test.actor",
        timestamp=timestamp,
        correlation_id="test-correlation-3",
    )

    # Assertions
    assert len(response.updated_suppliers) == 2
    assert response.validation_verdict == "fail"  # Below minimum of 3


def test_capture_adjustment_unknown_supplier_rejected(db_session):
    """Test that unknown suppliers are rejected."""
    # Create need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-004",
        channel_type="rfp",
        arrival_timestamp=pytest.now,
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.90,
        evidence_limited_flag=False,
        correlation_id="test-correlation-4",
    )
    db_session.add(need)
    db_session.commit()

    # Create longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        proposal_id=uuid.uuid4(),
        suppliers=json.dumps(["SUP-0231", "SUP-0118"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Attempt to add invalid supplier
    service = LonglistAdjustmentService(db_session)
    timestamp = datetime.utcnow()

    with pytest.raises(ValueError, match="Unknown supplier"):
        service.capture_adjustment(
            longlist_id=longlist.id,
            supplier_id="XX",  # Too short, invalid
            action="add",
            reason="Testing unknown supplier rejection",
            actor="test.actor",
            timestamp=timestamp,
            correlation_id="test-correlation-4",
        )


def test_capture_adjustment_invalid_action_rejected(db_session):
    """Test that invalid actions are rejected."""
    # Create need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-005",
        channel_type="rfp",
        arrival_timestamp=pytest.now,
        status="classified_it_service",
        classification_verdict="it_service",
        classification_confidence=0.93,
        evidence_limited_flag=False,
        correlation_id="test-correlation-5",
    )
    db_session.add(need)
    db_session.commit()

    # Create longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        proposal_id=uuid.uuid4(),
        suppliers=json.dumps(["SUP-0231", "SUP-0118"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Attempt invalid action
    service = LonglistAdjustmentService(db_session)
    timestamp = datetime.utcnow()

    with pytest.raises(ValueError, match="Invalid action"):
        service.capture_adjustment(
            longlist_id=longlist.id,
            supplier_id="SUP-0045",
            action="modify",  # Invalid action
            reason="Testing invalid action rejection",
            actor="test.actor",
            timestamp=timestamp,
            correlation_id="test-correlation-5",
        )


def test_capture_adjustment_longlist_not_found(db_session):
    """Test adjustment fails when longlist not found."""
    service = LonglistAdjustmentService(db_session)
    timestamp = datetime.utcnow()

    with pytest.raises(ValueError, match="Longlist .* not found"):
        service.capture_adjustment(
            longlist_id=uuid.uuid4(),
            supplier_id="SUP-0045",
            action="add",
            reason="Testing not found",
            actor="test.actor",
            timestamp=timestamp,
            correlation_id="test-correlation-6",
        )
