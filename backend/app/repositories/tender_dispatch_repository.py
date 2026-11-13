"""Repository for tender dispatch operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.tender_dispatch import TenderDispatch


class TenderDispatchRepository:
    """Repository for TenderDispatch CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, dispatch_id: UUID) -> Optional[TenderDispatch]:
        """Retrieve a tender dispatch by ID."""
        return self.session.query(TenderDispatch).filter(
            TenderDispatch.id == dispatch_id
        ).first()

    def get_by_batch_id(self, batch_id: str) -> List[TenderDispatch]:
        """Retrieve all dispatches for a batch."""
        return self.session.query(TenderDispatch).filter(
            TenderDispatch.dispatch_batch_id == batch_id
        ).all()

    def get_by_longlist_id(self, longlist_id: UUID) -> List[TenderDispatch]:
        """Retrieve all dispatches for a longlist."""
        return self.session.query(TenderDispatch).filter(
            TenderDispatch.longlist_id == longlist_id
        ).all()

    def create(self, dispatch: TenderDispatch) -> TenderDispatch:
        """Create a new tender dispatch record."""
        self.session.add(dispatch)
        self.session.commit()
        self.session.refresh(dispatch)
        return dispatch

    def update(self, dispatch: TenderDispatch) -> TenderDispatch:
        """Update an existing tender dispatch record."""
        self.session.commit()
        self.session.refresh(dispatch)
        return dispatch

    def get_all(self) -> List[TenderDispatch]:
        """Retrieve all tender dispatches."""
        return self.session.query(TenderDispatch).all()
