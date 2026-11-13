"""Repository for longlist adjustment operations."""

from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.longlist_adjustment import LonglistAdjustment


class LonglistAdjustmentRepository:
    """Repository for LonglistAdjustment CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, adjustment: LonglistAdjustment) -> LonglistAdjustment:
        """Create a new adjustment record."""
        self.session.add(adjustment)
        self.session.commit()
        self.session.refresh(adjustment)
        return adjustment

    def get_by_longlist_id(self, longlist_id: UUID) -> List[LonglistAdjustment]:
        """Retrieve all adjustments for a longlist."""
        return self.session.query(LonglistAdjustment).filter(
            LonglistAdjustment.longlist_id == longlist_id
        ).order_by(LonglistAdjustment.created_at).all()

    def count_by_longlist_id(self, longlist_id: UUID) -> int:
        """Count adjustments for a longlist."""
        return self.session.query(LonglistAdjustment).filter(
            LonglistAdjustment.longlist_id == longlist_id
        ).count()
