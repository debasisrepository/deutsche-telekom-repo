"""Unit tests for TenderDispatchService (ATS12)."""

import json
import uuid
from datetime import UTC, datetime

import pytest
from fastapi import HTTPException

from app.models.longlist import Longlist
from app.models.need import Need
from app.services.tender_dispatch_service import TenderDispatchService


def test_dispatch_tender_success(db_session):
    """Test successful tender dispatch to locked longlist."""
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
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307"]),
        locked=True,
        locked_at=datetime.now(UTC),
        locked_by="finalization_user",
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Dispatch tender
    service = TenderDispatchService(db_session)
    supplier_contacts = [
        {"supplier_id": "SUP-0231", "contact_email": "contact1@example.com", "contact_name": "Contact 1"},
        {"supplier_id": "SUP-0118", "contact_email": "contact2@example.com", "contact_name": "Contact 2"},
        {"supplier_id": "SUP-0307", "contact_email": "contact3@example.com", "contact_name": "Contact 3"},
    ]
    
    result = service.dispatch_tender(
        longlist_id=longlist.id,
        tender_template="TEMPLATE-001",
        supplier_contacts=supplier_contacts,
        correlation_id=str(uuid.uuid4()),
    )

    # Verify result
    assert "dispatch_batch_id" in result
    assert result["longlist_id"] == longlist.id
    assert len(result["supplier_dispatches"]) == 3
    
    # Verify each dispatch
    for dispatch in result["supplier_dispatches"]:
        assert "dispatch_id" in dispatch
        assert dispatch["supplier_id"] in ["SUP-0231", "SUP-0118", "SUP-0307"]
        assert "tender_package_ref" in dispatch
        assert dispatch["dispatch_status"] in ["delivered", "retrying", "pending"]


def test_dispatch_tender_longlist_not_locked(db_session):
    """Test dispatch rejection when longlist not locked."""
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

    # Create an unlocked longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Attempt dispatch should fail
    service = TenderDispatchService(db_session)
    supplier_contacts = [
        {"supplier_id": "SUP-0231", "contact_email": "contact1@example.com", "contact_name": "Contact 1"},
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        service.dispatch_tender(
            longlist_id=longlist.id,
            tender_template="TEMPLATE-001",
            supplier_contacts=supplier_contacts,
            correlation_id=str(uuid.uuid4()),
        )

    assert exc_info.value.status_code == 400
    assert "not locked" in exc_info.value.detail


def test_dispatch_tender_empty_longlist(db_session):
    """Test dispatch rejection when longlist empty."""
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

    # Create a locked but empty longlist
    longlist = Longlist(
        id=uuid.uuid4(),
        need_id=need.id,
        suppliers=json.dumps([]),
        locked=True,
        locked_at=datetime.now(UTC),
        locked_by="finalization_user",
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Attempt dispatch should fail
    service = TenderDispatchService(db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        service.dispatch_tender(
            longlist_id=longlist.id,
            tender_template="TEMPLATE-001",
            supplier_contacts=[],
            correlation_id=str(uuid.uuid4()),
        )

    assert exc_info.value.status_code == 400
    assert "no suppliers" in exc_info.value.detail


def test_dispatch_tender_missing_contacts(db_session):
    """Test dispatch rejection when supplier contacts missing."""
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
        suppliers=json.dumps(["SUP-0231", "SUP-0118", "SUP-0307"]),
        locked=True,
        locked_at=datetime.now(UTC),
        locked_by="finalization_user",
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # Attempt dispatch with missing contacts should fail
    service = TenderDispatchService(db_session)
    supplier_contacts = [
        {"supplier_id": "SUP-0231", "contact_email": "contact1@example.com", "contact_name": "Contact 1"},
        # SUP-0118 and SUP-0307 missing
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        service.dispatch_tender(
            longlist_id=longlist.id,
            tender_template="TEMPLATE-001",
            supplier_contacts=supplier_contacts,
            correlation_id=str(uuid.uuid4()),
        )

    assert exc_info.value.status_code == 400
    assert "missing contacts" in exc_info.value.detail
