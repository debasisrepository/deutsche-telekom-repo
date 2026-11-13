"""VMS handoff repository for data access."""
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.vms_handoff import VmsHandoff


class VmsHandoffRepository:
    """Repository for VmsHandoff CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, handoff: VmsHandoff) -> VmsHandoff:
        """Create a new VMS handoff record."""
        self.session.add(handoff)
        self.session.flush()
        self.session.refresh(handoff)
        return handoff

    def get_by_id(self, handoff_id: UUID) -> VmsHandoff | None:
        """Retrieve a VMS handoff by ID."""
        return self.session.query(VmsHandoff).filter(VmsHandoff.id == handoff_id).first()

    def get_by_need_id(self, need_id: UUID) -> VmsHandoff | None:
        """Retrieve the latest VMS handoff for a need."""
        return (
            self.session.query(VmsHandoff)
            .filter(VmsHandoff.need_id == need_id)
            .order_by(VmsHandoff.created_at.desc())
            .first()
        )

    def list_all(self, limit: int = 100) -> list[VmsHandoff]:
        """List all VMS handoffs ordered by created_at descending."""
        return (
            self.session.query(VmsHandoff)
            .order_by(VmsHandoff.created_at.desc())
            .limit(limit)
            .all()
        )

    def update(self, handoff: VmsHandoff) -> VmsHandoff:
        """Update an existing VMS handoff record."""
        self.session.flush()
        self.session.refresh(handoff)
        return handoff
