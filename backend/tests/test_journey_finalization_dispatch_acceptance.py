"""Journey J-03: Finalization and Dispatch acceptance tests.

Tests the complete user journey from supplier count validation (ATS9) through
longlist adjustments (ATS10), immutable lock (ATS11), and tender dispatch (ATS12),
covering features FR-009, FR-010, FR-011, and FR-012.
"""

import json
import uuid

import pytest


def test_j03_complete_finalization_and_dispatch_journey(auth_client, db_session):
    """Test complete J-03 journey: validation → lock → dispatch.

    Journey steps:
    - Setup: Create need with approved longlist proposal
    - ATS9: Validate supplier count (pass with 4 suppliers)
    - ATS11: Lock longlist immutably
    - ATS12: Dispatch tenders to all suppliers
    """
    from app.models.need import Need
    from app.models.longlist_proposal import LonglistProposal
    from app.models.longlist_ranked_supplier import LonglistRankedSupplier
    from datetime import datetime, UTC

    # Setup: Create need and proposal with 4 suppliers
    need_id = uuid.uuid4()
    need = Need(
        id=need_id,
        business_unit_id="BU-J03-TEST",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="s3://test/j03-need.pdf",
        normalized_payload_json=json.dumps({"title": "Infrastructure Services"}),
        status="proposal_reviewed",
        correlation_id="J03-001",
    )
    db_session.add(need)

    proposal_id = uuid.uuid4()
    proposal = LonglistProposal(
        id=proposal_id,
        need_id=need_id,
        ranked_suppliers=json.dumps(["SUP-J03-001", "SUP-J03-002", "SUP-J03-003", "SUP-J03-004"]),
        evidence_limited_flag=False,
        review_status="approved",
        reviewer_notes="Strong candidates",
    )
    db_session.add(proposal)

    # Add ranked suppliers with proper citations
    for i, supplier_id in enumerate(["SUP-J03-001", "SUP-J03-002", "SUP-J03-003", "SUP-J03-004"], start=1):
        ranked = LonglistRankedSupplier(
            id=uuid.uuid4(),
            proposal_id=proposal_id,
            supplier_id=supplier_id,
            rank=i,
            panel_source=f"PANEL-{i}",
            evidence_citations=json.dumps([f"CITATION-{supplier_id}"]),
            rank_rationale=f"Supplier {i} rationale",
            confidence=0.80 + (i * 0.02),
        )
        db_session.add(ranked)

    db_session.commit()

    # ATS9: Validate supplier count
    validation_payload = {
        "supplier_ids": ["SUP-J03-001", "SUP-J03-002", "SUP-J03-003", "SUP-J03-004"]
    }

    validation_resp = auth_client.post(
        f"/api/v1/longlists/{proposal_id}/validate-count",
        json=validation_payload,
        headers={"X-Correlation-Id": "J03-001"}
    )
    assert validation_resp.status_code == 200, f"Validation failed: {validation_resp.text}"
    validation_data = validation_resp.json()
    assert validation_data["validation_verdict"] == "pass"
    assert validation_data["supplier_count"] == 4

    # ATS11: Lock longlist
    lock_payload = {
        "expected_validation_verdict": "pass",
        "supplier_ids": ["SUP-J03-001", "SUP-J03-002", "SUP-J03-003", "SUP-J03-004"],
        "finalized_by": "longlist_finalization_owner@example.com"
    }

    lock_resp = auth_client.post(
        f"/api/v1/longlists/{proposal_id}/lock",
        json=lock_payload,
        headers={"X-Correlation-Id": "J03-001"}
    )
    assert lock_resp.status_code == 200, f"Lock failed: {lock_resp.text}"
    lock_data = lock_resp.json()
    assert lock_data["locked"] is True
    assert lock_data["need_id"] == str(need_id)
    longlist_id = lock_data["longlist_id"]

    # ATS12: Dispatch tenders
    dispatch_payload = {
        "longlist_id": longlist_id,
        "tender_template": "standard-template-v1",
        "supplier_contacts": [
            {"supplier_id": "SUP-J03-001", "contact_email": "contact1@sup-j03-001.example.com"},
            {"supplier_id": "SUP-J03-002", "contact_email": "contact2@sup-j03-002.example.com"},
            {"supplier_id": "SUP-J03-003", "contact_email": "contact3@sup-j03-003.example.com"},
            {"supplier_id": "SUP-J03-004", "contact_email": "contact4@sup-j03-004.example.com"},
        ]
    }

    dispatch_resp = auth_client.post(
        "/api/v1/tenders/dispatch",
        json=dispatch_payload,
        headers={"X-Correlation-Id": "J03-001"}
    )
    assert dispatch_resp.status_code == 201, f"Dispatch failed: {dispatch_resp.text}"
    dispatch_data = dispatch_resp.json()
    assert "dispatch_batch_id" in dispatch_data
    assert dispatch_data["longlist_id"] == longlist_id
    assert len(dispatch_data["supplier_dispatches"]) == 4
    # All dispatches should have a status
    for dispatch in dispatch_data["supplier_dispatches"]:
        assert dispatch["dispatch_status"] in ["pending", "delivered", "retrying"]


def test_j03_journey_with_adjustment(auth_client, db_session):
    """Test J-03 journey with ATS10 longlist adjustment.

    Journey steps:
    - Setup: Create proposal with 3 suppliers
    - ATS9: Validate (pass with 3)
    - ATS10: Add one supplier (adjustment)
    - ATS9: Revalidate (pass with 4)
    - ATS11: Lock
    - ATS12: Dispatch
    """
    from app.models.need import Need
    from app.models.longlist_proposal import LonglistProposal
    from app.models.longlist_ranked_supplier import LonglistRankedSupplier
    from app.models.longlist import Longlist
    from datetime import datetime, UTC

    # Setup
    need_id = uuid.uuid4()
    need = Need(
        id=need_id,
        business_unit_id="BU-J03-ADJ",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="s3://test/j03-adj.pdf",
        normalized_payload_json=json.dumps({"title": "Platform Services"}),
        status="proposal_reviewed",
        correlation_id="J03-ADJ-001",
    )
    db_session.add(need)

    proposal_id = uuid.uuid4()
    proposal = LonglistProposal(
        id=proposal_id,
        need_id=need_id,
        ranked_suppliers=json.dumps(["SUP-ADJ-001", "SUP-ADJ-002", "SUP-ADJ-003"]),
        evidence_limited_flag=False,
        review_status="approved",
        reviewer_notes="Initial proposal",
    )
    db_session.add(proposal)

    for i, supplier_id in enumerate(["SUP-ADJ-001", "SUP-ADJ-002", "SUP-ADJ-003"], start=1):
        ranked = LonglistRankedSupplier(
            id=uuid.uuid4(),
            proposal_id=proposal_id,
            supplier_id=supplier_id,
            rank=i,
            panel_source=f"PANEL-{i}",
            evidence_citations=json.dumps([f"CITATION-{supplier_id}"]),
            rank_rationale=f"Supplier {i}",
            confidence=0.80,
        )
        db_session.add(ranked)

    db_session.commit()

    # ATS9: Initial validation (pass with 3)
    validation_resp = auth_client.post(
        f"/api/v1/longlists/{proposal_id}/validate-count",
        json={"supplier_ids": ["SUP-ADJ-001", "SUP-ADJ-002", "SUP-ADJ-003"]},
        headers={"X-Correlation-Id": "J03-ADJ-001"}
    )
    assert validation_resp.status_code == 200
    assert validation_resp.json()["validation_verdict"] == "pass"

    # Create unlocked longlist for adjustment
    longlist_id = uuid.uuid4()
    longlist = Longlist(
        id=longlist_id,
        need_id=need_id,
        proposal_id=proposal_id,
        suppliers=json.dumps(["SUP-ADJ-001", "SUP-ADJ-002", "SUP-ADJ-003"]),
        locked=False,
        change_history=json.dumps([]),
    )
    db_session.add(longlist)
    db_session.commit()

    # ATS10: Add supplier via adjustment
    adjustment_payload = {
        "supplier_id": "SUP-ADJ-004",
        "action": "add",
        "reason": "Business unit requested additional qualified supplier",
        "actor": "business_unit_collaborator@example.com"
    }

    adjustment_resp = auth_client.post(
        f"/api/v1/longlists/{longlist_id}/adjustments",
        json=adjustment_payload,
        headers={"X-Correlation-Id": "J03-ADJ-001"}
    )
    assert adjustment_resp.status_code == 201, f"Adjustment failed: {adjustment_resp.text}"
    adjustment_data = adjustment_resp.json()
    assert adjustment_data["validation_verdict"] == "pass"  # Revalidation after adjustment
    assert len(adjustment_data["updated_suppliers"]) == 4

    # ATS11: Lock with updated supplier list
    lock_resp = auth_client.post(
        f"/api/v1/longlists/{longlist_id}/lock",
        json={
            "expected_validation_verdict": "pass",
            "supplier_ids": ["SUP-ADJ-001", "SUP-ADJ-002", "SUP-ADJ-003", "SUP-ADJ-004"],
            "finalized_by": "longlist_finalization_owner@example.com"
        },
        headers={"X-Correlation-Id": "J03-ADJ-001"}
    )
    assert lock_resp.status_code == 200
    lock_data = lock_resp.json()
    assert lock_data["locked"] is True

    # ATS12: Dispatch to all 4 suppliers
    dispatch_resp = auth_client.post(
        "/api/v1/tenders/dispatch",
        json={
            "longlist_id": str(longlist_id),
            "tender_template": "standard-template-v1",
            "supplier_contacts": [
                {"supplier_id": f"SUP-ADJ-{str(i).zfill(3)}", "contact_email": f"contact@sup-adj-{str(i).zfill(3)}.example.com"}
                for i in range(1, 5)
            ]
        },
        headers={"X-Correlation-Id": "J03-ADJ-001"}
    )
    assert dispatch_resp.status_code == 201
    assert len(dispatch_resp.json()["supplier_dispatches"]) == 4


def test_j03_validation_failure_blocks_lock(auth_client, db_session):
    """Test that ATS9 validation failure blocks ATS11 lock."""
    from app.models.need import Need
    from app.models.longlist_proposal import LonglistProposal
    from app.models.longlist_ranked_supplier import LonglistRankedSupplier
    from datetime import datetime, UTC

    # Setup with only 2 suppliers (below minimum)
    need_id = uuid.uuid4()
    need = Need(
        id=need_id,
        business_unit_id="BU-J03-FAIL",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="s3://test/j03-fail.pdf",
        normalized_payload_json=json.dumps({"title": "Test Service"}),
        status="proposal_reviewed",
        correlation_id="J03-FAIL-001",
    )
    db_session.add(need)

    proposal_id = uuid.uuid4()
    proposal = LonglistProposal(
        id=proposal_id,
        need_id=need_id,
        ranked_suppliers=json.dumps(["SUP-FAIL-001", "SUP-FAIL-002"]),
        evidence_limited_flag=False,
        review_status="approved",
        reviewer_notes="Only 2 suppliers found",
    )
    db_session.add(proposal)

    for i, supplier_id in enumerate(["SUP-FAIL-001", "SUP-FAIL-002"], start=1):
        ranked = LonglistRankedSupplier(
            id=uuid.uuid4(),
            proposal_id=proposal_id,
            supplier_id=supplier_id,
            rank=i,
            panel_source=f"PANEL-{i}",
            evidence_citations=json.dumps([f"CITATION-{supplier_id}"]),
            rank_rationale=f"Supplier {i}",
            confidence=0.75,
        )
        db_session.add(ranked)

    db_session.commit()

    # ATS9: Validate (should fail with 2 suppliers)
    validation_resp = auth_client.post(
        f"/api/v1/longlists/{proposal_id}/validate-count",
        json={"supplier_ids": ["SUP-FAIL-001", "SUP-FAIL-002"]},
        headers={"X-Correlation-Id": "J03-FAIL-001"}
    )
    assert validation_resp.status_code == 200
    validation_data = validation_resp.json()
    assert validation_data["validation_verdict"] == "fail"
    assert validation_data["supplier_count"] == 2

    # ATS11: Attempt to lock should fail
    lock_resp = auth_client.post(
        f"/api/v1/longlists/{proposal_id}/lock",
        json={
            "expected_validation_verdict": "pass",  # Wrong expectation
            "supplier_ids": ["SUP-FAIL-001", "SUP-FAIL-002"],
            "finalized_by": "longlist_finalization_owner@example.com"
        },
        headers={"X-Correlation-Id": "J03-FAIL-001"}
    )
    # Lock should be rejected due to validation failure
    assert lock_resp.status_code in [400, 409], f"Lock should fail, got: {lock_resp.status_code}"


def test_j03_validation_too_many_suppliers_blocks_lock(auth_client, db_session):
    """Test that ATS9 validation fails when supplier count exceeds maximum (7 > 6)."""
    from app.models.need import Need
    from app.models.longlist_proposal import LonglistProposal
    from app.models.longlist_ranked_supplier import LonglistRankedSupplier
    from datetime import datetime, UTC

    # Setup with 7 suppliers (above maximum of 6)
    need_id = uuid.uuid4()
    need = Need(
        id=need_id,
        business_unit_id="BU-J03-TOOMANY",
        channel_type="rfp",
        arrival_timestamp=datetime.now(UTC),
        raw_artifact_ref="s3://test/j03-toomany.pdf",
        normalized_payload_json=json.dumps({"title": "Large Service"}),
        status="proposal_reviewed",
        correlation_id="J03-TOOMANY-001",
    )
    db_session.add(need)

    supplier_ids = [f"SUP-MANY-{str(i).zfill(3)}" for i in range(1, 8)]
    proposal_id = uuid.uuid4()
    proposal = LonglistProposal(
        id=proposal_id,
        need_id=need_id,
        ranked_suppliers=json.dumps(supplier_ids),
        evidence_limited_flag=False,
        review_status="approved",
        reviewer_notes="7 suppliers identified",
    )
    db_session.add(proposal)

    for i, supplier_id in enumerate(supplier_ids, start=1):
        ranked = LonglistRankedSupplier(
            id=uuid.uuid4(),
            proposal_id=proposal_id,
            supplier_id=supplier_id,
            rank=i,
            panel_source=f"PANEL-{i}",
            evidence_citations=json.dumps([f"CITATION-{supplier_id}"]),
            rank_rationale=f"Supplier {i}",
            confidence=0.70,
        )
        db_session.add(ranked)

    db_session.commit()

    # ATS9: Validate (should fail with 7 suppliers, max is 6)
    validation_resp = auth_client.post(
        f"/api/v1/longlists/{proposal_id}/validate-count",
        json={"supplier_ids": supplier_ids},
        headers={"X-Correlation-Id": "J03-TOOMANY-001"}
    )
    assert validation_resp.status_code == 200
    validation_data = validation_resp.json()
    assert validation_data["validation_verdict"] == "fail"
    assert validation_data["supplier_count"] == 7
    assert len(validation_data["violations"]) > 0
