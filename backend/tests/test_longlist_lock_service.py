"""Unit tests for LonglistLockService (ATS11)."""

import json
import uuid
from datetime import UTC, datetime

import pytest
from fastapi import HTTPException

from app.models.longlist import Longlist
from app.models.need import Need
from app.services.longlist_lock_service import LonglistLockService


def test_lock_longlist_success(db_session):
    """Test successful longlist lock with passing validation."""
    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-artifact",
        normalized_payload_json="{}",
        status="classified_it_service",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Create an unlocked longlist with 4 suppliers (valid count)
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Lock the longlist
    service = LonglistLockService(db_session)
    result = service.lock_longlist(
        longlist_id=longlist.id,
        expected_validation_verdict="pass",
        supplier_ids=["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"],
        finalized_by="finalization_user",
        correlation_id=str(uuid.uuid4()),
    )

    # Verify result
    assert result["longlist_id"] == longlist.id
    assert result["need_id"] == need.id
    assert result["locked"] is True
    assert result["locked_at"] is not None
    assert result["validation_count"] == 4
    assert len(result["suppliers"]) == 4

    # Verify longlist was updated
    db_session.refresh(longlist)
    assert longlist.locked is True
    assert longlist.locked_by == "finalization_user"
    assert longlist.validation_verdict_at_lock == "pass"


def test_lock_longlist_validation_fails(db_session):
    """Test lock rejection when validation fails (too few suppliers)."""
    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-artifact",
        normalized_payload_json="{}",
        status="classified_it_service",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Create an unlocked longlist with 2 suppliers (below minimum)
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        suppliers=json.dumps(["SUP-0231", "SUP-0118"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Attempt to lock should fail
    service = LonglistLockService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.lock_longlist(
            longlist_id=longlist.id,
            expected_validation_verdict="pass",
            supplier_ids=["SUP-0231", "SUP-0118"],
            finalized_by="finalization_user",
            correlation_id=str(uuid.uuid4()),
        )

    assert exc_info.value.status_code == 400
    assert "validation verdict is 'fail'" in exc_info.value.detail

    # Verify longlist was NOT locked
    db_session.refresh(longlist)
    assert longlist.locked is False


def test_lock_longlist_already_locked(db_session):
    """Test lock rejection when longlist already locked."""
    # Create a need
    need = Need(
        id=uuid.uuid4(),
        business_unit_id="BU-001",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="test-artifact",
        normalized_payload_json="{}",
        status="classified_it_service",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(need)
    db_session.commit()

    # Create a locked longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"]),
        locked=True,
        locked_at=datetime.now(UTC),
        locked_by="original_user",
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Attempt to lock again should fail
    service = LonglistLockService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.lock_longlist(
            longlist_id=longlist.id,
            expected_validation_verdict="pass",
            supplier_ids=["SUP-0231", "SUP-0118", "SUP-0307", "SUP-0045"],
            finalized_by="finalization_user",
            correlation_id=str(uuid.uuid4()),
        )

    assert exc_info.value.status_code == 400
    assert "already locked" in exc_info.value.detail


def test_lock_longlist_not_found(db_session):
    """Test lock rejection when longlist not found."""
    service = LonglistLockService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        service.lock_longlist(
            longlist_id=uuid.uuid4(),
            expected_validation_verdict="pass",
            supplier_ids=["SUP-0231", "SUP-0118", "SUP-0307"],
            finalized_by="finalization_user",
            correlation_id=str(uuid.uuid4()),
        )

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail
