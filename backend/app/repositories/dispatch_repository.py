"""Dispatch Repository - Data access for tender dispatch records."""
from sqlalchemy.orm import Session

from app.models.tender_dispatch import TenderDispatch
from app.models.tender_dispatch_recipient import TenderDispatchRecipient


class DispatchRepository:
    """Repository for tender dispatch data access."""

    def __init__(self, session: Session):
        self.session = session

    def create_tender_dispatch(
        self,
        locked_longlist_id: int,
        dispatch_batch_ref: str,
        dispatch_status: str,
        dispatched_by: str,
        requirement_tags: str | None = None
    ) -> TenderDispatch:
        """Create tender dispatch record.
        
        Args:
            locked_longlist_id: Locked longlist identifier
            dispatch_batch_ref: Unique batch reference
            dispatch_status: Dispatch status (success, partial_failure, failed)
            dispatched_by: Actor performing dispatch
            requirement_tags: Requirement tags
            
        Returns:
            TenderDispatch instance
        """
        tender_dispatch = TenderDispatch(
            locked_longlist_id=locked_longlist_id,
            dispatch_batch_ref=dispatch_batch_ref,
            dispatch_status=dispatch_status,
            dispatched_by=dispatched_by,
            requirement_tags=requirement_tags
        )
        self.session.add(tender_dispatch)
        self.session.flush()
        return tender_dispatch

    def create_dispatch_recipient(
        self,
        dispatch_id: int,
        supplier_id: int,
        delivery_status: str,
        external_delivery_ref: str | None = None,
        requirement_tags: str | None = None
    ) -> TenderDispatchRecipient:
        """Create dispatch recipient record.
        
        Args:
            dispatch_id: Dispatch identifier
            supplier_id: Supplier identifier
            delivery_status: Delivery status (success, failed)
            external_delivery_ref: External delivery reference from TOL6
            requirement_tags: Requirement tags
            
        Returns:
            TenderDispatchRecipient instance
        """
        recipient = TenderDispatchRecipient(
            dispatch_id=dispatch_id,
            supplier_id=supplier_id,
            delivery_status=delivery_status,
            external_delivery_ref=external_delivery_ref,
            requirement_tags=requirement_tags
        )
        self.session.add(recipient)
        self.session.flush()
        return recipient

    def get_tender_dispatch_by_locked_longlist(
        self,
        locked_longlist_id: int
    ) -> TenderDispatch | None:
        """Get tender dispatch by locked longlist ID.
        
        Args:
            locked_longlist_id: Locked longlist identifier
            
        Returns:
            TenderDispatch instance or None
        """
        return self.session.query(TenderDispatch).filter_by(
            locked_longlist_id=locked_longlist_id
        ).first()

    def list_dispatch_recipients(self, dispatch_id: int) -> list[TenderDispatchRecipient]:
        """List all recipients for a dispatch.
        
        Args:
            dispatch_id: Dispatch identifier
            
        Returns:
            List of TenderDispatchRecipient instances
        """
        return self.session.query(TenderDispatchRecipient).filter_by(
            dispatch_id=dispatch_id
        ).all()
