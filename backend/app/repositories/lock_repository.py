"""Lock Repository - Data access for locked longlist records."""
from sqlalchemy.orm import Session

from app.models.locked_longlist import LockedLonglist
from app.models.locked_supplier import LockedSupplier


class LockRepository:
    """Repository for locked longlist data access."""

    def __init__(self, session: Session):
        self.session = session

    def create_locked_longlist(
        self,
        case_id: int,
        source_proposal_id: int,
        lock_status: str,
        locked_by: str,
        requirement_tags: str | None = None
    ) -> LockedLonglist:
        """Create locked longlist record.
        
        Args:
            case_id: Case identifier
            source_proposal_id: Source proposal identifier
            lock_status: Lock status (locked, unlocked)
            locked_by: Actor performing lock
            requirement_tags: Requirement tags
            
        Returns:
            LockedLonglist instance
        """
        locked_longlist = LockedLonglist(
            case_id=case_id,
            source_proposal_id=source_proposal_id,
            lock_status=lock_status,
            locked_by=locked_by,
            requirement_tags=requirement_tags
        )
        self.session.add(locked_longlist)
        self.session.flush()
        return locked_longlist

    def create_locked_supplier(
        self,
        locked_longlist_id: int,
        supplier_id: int,
        final_rank_position: int,
        requirement_tags: str | None = None
    ) -> LockedSupplier:
        """Create locked supplier record.
        
        Args:
            locked_longlist_id: Locked longlist identifier
            supplier_id: Supplier identifier
            final_rank_position: Final rank position from proposal
            requirement_tags: Requirement tags
            
        Returns:
            LockedSupplier instance
        """
        locked_supplier = LockedSupplier(
            locked_longlist_id=locked_longlist_id,
            supplier_id=supplier_id,
            final_rank_position=final_rank_position,
            requirement_tags=requirement_tags
        )
        self.session.add(locked_supplier)
        self.session.flush()
        return locked_supplier

    def get_locked_longlist_by_case(self, case_id: int) -> LockedLonglist | None:
        """Get locked longlist by case ID.
        
        Args:
            case_id: Case identifier
            
        Returns:
            LockedLonglist instance or None
        """
        return self.session.query(LockedLonglist).filter_by(case_id=case_id).first()

    def list_locked_suppliers(self, locked_longlist_id: int) -> list[LockedSupplier]:
        """List all locked suppliers for a locked longlist.
        
        Args:
            locked_longlist_id: Locked longlist identifier
            
        Returns:
            List of LockedSupplier instances ordered by rank
        """
        return self.session.query(LockedSupplier).filter_by(
            locked_longlist_id=locked_longlist_id
        ).order_by(LockedSupplier.final_rank_position).all()
