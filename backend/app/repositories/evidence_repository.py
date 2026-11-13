import uuid
from typing import List

from sqlalchemy.orm import Session

from app.models.supplier_evidence_item import SupplierEvidenceItem


class EvidenceRepository:
    """Repository for evidence item data access."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_need_id(self, need_id: uuid.UUID) -> List[SupplierEvidenceItem]:
        """Retrieve all evidence items for a given need."""
        return self.session.query(SupplierEvidenceItem).filter(
            SupplierEvidenceItem.need_id == need_id
        ).all()

    def create(self, evidence_item: SupplierEvidenceItem) -> SupplierEvidenceItem:
        """Create a new evidence item."""
        self.session.add(evidence_item)
        self.session.commit()
        self.session.refresh(evidence_item)
        return evidence_item

    def create_many(self, evidence_items: List[SupplierEvidenceItem]) -> List[SupplierEvidenceItem]:
        """Create multiple evidence items in bulk."""
        self.session.add_all(evidence_items)
        self.session.commit()
        for item in evidence_items:
            self.session.refresh(item)
        return evidence_items

    def filter_by_supplier(self, need_id: uuid.UUID, supplier_id: str) -> List[SupplierEvidenceItem]:
        """Filter evidence items by supplier ID."""
        return self.session.query(SupplierEvidenceItem).filter(
            SupplierEvidenceItem.need_id == need_id,
            SupplierEvidenceItem.supplier_id == supplier_id
        ).all()
