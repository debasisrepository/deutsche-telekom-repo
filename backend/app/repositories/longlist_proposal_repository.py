"""Repository for longlist proposal operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.longlist_proposal import LonglistProposal


class LonglistProposalRepository:
    """Repository for LonglistProposal CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, proposal_id: UUID) -> Optional[LonglistProposal]:
        """Retrieve a proposal by ID."""
        return self.session.query(LonglistProposal).filter(
            LonglistProposal.id == proposal_id
        ).first()

    def get_by_need_id(self, need_id: UUID) -> Optional[LonglistProposal]:
        """Retrieve a proposal by need ID."""
        return self.session.query(LonglistProposal).filter(
            LonglistProposal.need_id == need_id
        ).first()

    def create(self, proposal: LonglistProposal) -> LonglistProposal:
        """Create a new proposal."""
        self.session.add(proposal)
        self.session.commit()
        self.session.refresh(proposal)
        return proposal

    def update(self, proposal: LonglistProposal) -> LonglistProposal:
        """Update an existing proposal."""
        self.session.commit()
        self.session.refresh(proposal)
        return proposal

    def get_all(self) -> List[LonglistProposal]:
        """Retrieve all proposals."""
        return self.session.query(LonglistProposal).all()
