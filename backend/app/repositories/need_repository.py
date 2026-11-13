"""Need repository for data access."""
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.need import Need


class NeedRepository:
    """Repository for Need CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, need: Need) -> Need:
        """Create a new need record."""
        self.session.add(need)
        self.session.flush()
        self.session.refresh(need)
        return need

    def get_by_id(self, need_id: UUID) -> Need | None:
        """Retrieve a need by ID."""
        return self.session.query(Need).filter(Need.id == need_id).first()

    def update(self, need: Need) -> Need:
        """Update an existing need record."""
        self.session.flush()
        self.session.refresh(need)
        return need

    def list_all(self, limit: int = 100) -> list[Need]:
        """List all needs ordered by arrival_timestamp descending."""
        return (
            self.session.query(Need)
            .order_by(Need.arrival_timestamp.desc())
            .limit(limit)
            .all()
        )
