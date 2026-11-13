import json
import uuid
from datetime import UTC, datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.adapters.tol4_validation_util import TOL4ValidationUtil
from app.models.supplier_count_validation import SupplierCountValidation
from app.repositories.supplier_count_validation_repository import (
    SupplierCountValidationRepository,
)
from app.schemas.governance_schemas import SupplierCountValidationResponse


class SupplierCountValidationService:
    """
    Service for ATS9: Validate longlist supplier count against business rules.

    Enforces the deterministic 3-6 supplier count rule:
    - Pass: 3 <= count <= 6
    - Fail: count < 3 or count > 6
    """

    def __init__(self, session: Session):
        self.session = session
        self.validation_repo = SupplierCountValidationRepository(session)
        self.tol4_util = TOL4ValidationUtil()

    def validate_count(
        self,
        proposal_or_longlist_id: str,
        supplier_ids: List[str],
        correlation_id: Optional[str] = None,
    ) -> SupplierCountValidationResponse:
        """
        Validate supplier count against 3-6 rule (ATS9).

        Args:
            proposal_or_longlist_id: Proposal or longlist ID to validate
            supplier_ids: List of supplier IDs in the longlist
            correlation_id: Optional correlation ID for audit trail

        Returns:
            SupplierCountValidationResponse with verdict (pass|fail) and violations
        """
        proposal_uuid = uuid.UUID(proposal_or_longlist_id)
        supplier_count = len(supplier_ids)

        validation_result = self.tol4_util.validate_supplier_count(supplier_count)

        verdict = validation_result["verdict"]
        violations = validation_result["violations"]

        validation_record = SupplierCountValidation(
            id=uuid.uuid4(),
            proposal_id=proposal_uuid,
            supplier_count=supplier_count,
            validation_verdict=verdict,
            violations=json.dumps(violations) if violations else None,
            triggered_by="ATS9",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.validation_repo.create(validation_record)

        return SupplierCountValidationResponse(
            proposal_id=proposal_or_longlist_id,
            supplier_count=supplier_count,
            validation_verdict=verdict,
            violations=violations,
            validated_at=validation_record.created_at,
            correlation_id=correlation_id,
        )
