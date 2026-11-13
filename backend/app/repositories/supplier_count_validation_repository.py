import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.supplier_count_validation import SupplierCountValidation


class SupplierCountValidationRepository:
    """Repository for supplier count validation data access."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, validation_id: uuid.UUID) -> Optional[SupplierCountValidation]:
        """Retrieve a validation by ID."""
        return self.session.query(SupplierCountValidation).filter(
            SupplierCountValidation.id == validation_id
        ).first()

    def get_by_proposal_id(self, proposal_id: uuid.UUID) -> List[SupplierCountValidation]:
        """Retrieve all validations for a proposal."""
        return self.session.query(SupplierCountValidation).filter(
            SupplierCountValidation.proposal_id == proposal_id
        ).order_by(SupplierCountValidation.created_at.desc()).all()

    def get_latest_by_proposal_id(self, proposal_id: uuid.UUID) -> Optional[SupplierCountValidation]:
        """Retrieve the latest validation for a proposal."""
        return self.session.query(SupplierCountValidation).filter(
            SupplierCountValidation.proposal_id == proposal_id
        ).order_by(SupplierCountValidation.created_at.desc()).first()

    def create(self, validation: SupplierCountValidation) -> SupplierCountValidation:
        """Create a new validation record."""
        self.session.add(validation)
        self.session.commit()
        self.session.refresh(validation)
        return validation
