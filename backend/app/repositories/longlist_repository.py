"""Repository for longlist operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.longlist import Longlist


class LonglistRepository:
    """Repository for Longlist CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, longlist_id: UUID) -> Optional[Longlist]:
        """Retrieve a longlist by ID."""
        return self.session.query(Longlist).filter(
            Longlist.id == longlist_id
        ).first()

    def get_by_need_id(self, need_id: UUID) -> Optional[Longlist]:
        """Retrieve a longlist by need ID."""
        return self.session.query(Longlist).filter(
            Longlist.need_id == need_id
        ).first()

    def create(self, longlist: Longlist) -> Longlist:
        """Create a new longlist."""
        self.session.add(longlist)
        self.session.commit()
        self.session.refresh(longlist)
        return longlist

    def update(self, longlist: Longlist) -> Longlist:
        """Update an existing longlist."""
        self.session.commit()
        self.session.refresh(longlist)
        return longlist

    def get_all(self) -> List[Longlist]:
        """Retrieve all longlists."""
        return self.session.query(Longlist).all()
