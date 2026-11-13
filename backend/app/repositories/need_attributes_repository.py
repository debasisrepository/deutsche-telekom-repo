"""NeedAttributes repository for data access."""
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.need_attributes import NeedAttributes


class NeedAttributesRepository:
    """Repository for NeedAttributes CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, attrs: NeedAttributes) -> NeedAttributes:
        """Create a new need_attributes record."""
        self.session.add(attrs)
        self.session.flush()
        self.session.refresh(attrs)
        return attrs

    def get_by_need_id(self, need_id: UUID) -> NeedAttributes | None:
        """Retrieve need_attributes by need_id."""
        return self.session.query(NeedAttributes).filter(NeedAttributes.need_id == need_id).first()

    def update(self, attrs: NeedAttributes) -> NeedAttributes:
        """Update an existing need_attributes record."""
        self.session.flush()
        self.session.refresh(attrs)
        return attrs
