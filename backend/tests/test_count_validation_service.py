import uuid

import pytest

from app.services.supplier_count_validation_service import (
    SupplierCountValidationService,
)


def test_validate_count_pass_with_3_suppliers(db_session):
    """Test validation passes with exactly 3 suppliers (minimum)."""
    service = SupplierCountValidationService(db_session)
    proposal_id = uuid.uuid4()

    result = service.validate_count(
        proposal_or_longlist_id=str(proposal_id),
        supplier_ids=["SUP-001", "SUP-002", "SUP-003"],
    )

    assert result.validation_verdict == "pass"
    assert result.supplier_count == 3
    assert len(result.violations) == 0


def test_validate_count_pass_with_6_suppliers(db_session):
    """Test validation passes with exactly 6 suppliers (maximum)."""
    service = SupplierCountValidationService(db_session)
    proposal_id = uuid.uuid4()

    result = service.validate_count(
        proposal_or_longlist_id=str(proposal_id),
        supplier_ids=["SUP-001", "SUP-002", "SUP-003", "SUP-004", "SUP-005", "SUP-006"],
    )

    assert result.validation_verdict == "pass"
    assert result.supplier_count == 6
    assert len(result.violations) == 0


def test_validate_count_fail_with_2_suppliers(db_session):
    """Test validation fails with 2 suppliers (below minimum)."""
    service = SupplierCountValidationService(db_session)
    proposal_id = uuid.uuid4()

    result = service.validate_count(
        proposal_or_longlist_id=str(proposal_id),
        supplier_ids=["SUP-001", "SUP-002"],
    )

    assert result.validation_verdict == "fail"
    assert result.supplier_count == 2
    assert len(result.violations) == 1
    assert "below minimum" in result.violations[0]


def test_validate_count_fail_with_7_suppliers(db_session):
    """Test validation fails with 7 suppliers (above maximum)."""
    service = SupplierCountValidationService(db_session)
    proposal_id = uuid.uuid4()

    result = service.validate_count(
        proposal_or_longlist_id=str(proposal_id),
        supplier_ids=[f"SUP-{i:03d}" for i in range(1, 8)],
    )

    assert result.validation_verdict == "fail"
    assert result.supplier_count == 7
    assert len(result.violations) == 1
    assert "exceeds maximum" in result.violations[0]


def test_validate_count_pass_with_5_suppliers(db_session):
    """Test validation passes with 5 suppliers (middle of range)."""
    service = SupplierCountValidationService(db_session)
    proposal_id = uuid.uuid4()

    result = service.validate_count(
        proposal_or_longlist_id=str(proposal_id),
        supplier_ids=["SUP-001", "SUP-002", "SUP-003", "SUP-004", "SUP-005"],
    )

    assert result.validation_verdict == "pass"
    assert result.supplier_count == 5
    assert len(result.violations) == 0


def test_validate_count_creates_validation_record(db_session):
    """Test validation creates a persistent validation record."""
    service = SupplierCountValidationService(db_session)
    proposal_id = uuid.uuid4()

    result = service.validate_count(
        proposal_or_longlist_id=str(proposal_id),
        supplier_ids=["SUP-001", "SUP-002", "SUP-003", "SUP-004"],
    )

    latest_validation = service.validation_repo.get_latest_by_proposal_id(proposal_id)
    assert latest_validation is not None
    assert latest_validation.supplier_count == 4
    assert latest_validation.validation_verdict == "pass"
