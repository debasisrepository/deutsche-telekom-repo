"""AGN3 Service - Longlist Finalization and Tender Agent (ATS10, ATS11, ATS12)."""
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.adapters.tol6_tender_dispatch_adapter import TOL6TenderDispatchAdapter
from app.models.supplier_adjustment import SupplierAdjustment
from app.repositories.dispatch_repository import DispatchRepository
from app.repositories.lock_repository import LockRepository
from app.repositories.longlist_repository import LonglistRepository


class AGN3Service:
    """
    AGN3 Longlist Finalization and Tender Agent.
    
    Handles ATS10 (adjustment capture), ATS11 (locking), ATS12 (dispatch coordination).
    This service manages supplier adjustments and recalculates supplier counts.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.longlist_repo = LonglistRepository(session)
        self.lock_repo = LockRepository(session)
        self.dispatch_repo = DispatchRepository(session)
        self.tol6_adapter = TOL6TenderDispatchAdapter()
    
    def capture_adjustment(
        self,
        case_id: int,
        supplier_id: int,
        change_type: str,
        rationale: str | None,
        actor_id: str
    ) -> dict[str, Any]:
        """
        Capture supplier adjustment action (ATS10).
        
        Records add/remove supplier actions with actor, timestamp, rationale,
        and recalculates the resulting supplier count.
        
        Args:
            case_id: Case identifier
            supplier_id: Supplier being added or removed
            change_type: 'add' or 'remove'
            rationale: Business rationale for the adjustment
            actor_id: User ID or system identifier making the change
            
        Returns:
            Adjustment result dictionary with adjustment_id and resulting_supplier_count
        """
        if change_type not in ("add", "remove"):
            raise ValueError(f"Invalid change_type: {change_type}. Must be 'add' or 'remove'")
        
        # Get current proposal to calculate resulting count
        proposals = self.longlist_repo.list_case_proposals(case_id)
        if not proposals:
            raise ValueError(f"No longlist proposal found for case {case_id}")
        proposal = proposals[0]  # Get latest (already ordered by version_no desc)
        
        # Calculate resulting supplier count
        current_suppliers = self.longlist_repo.get_proposal_suppliers(proposal.id)
        current_count = len(current_suppliers)
        
        if change_type == "add":
            # Check if supplier already in proposal
            if any(ps.supplier_id == supplier_id for ps in current_suppliers):
                resulting_count = current_count
            else:
                resulting_count = current_count + 1
        else:  # remove
            # Check if supplier is in proposal
            if any(ps.supplier_id == supplier_id for ps in current_suppliers):
                resulting_count = current_count - 1
            else:
                resulting_count = current_count
        
        # Create adjustment record
        adjustment = SupplierAdjustment(
            case_id=case_id,
            supplier_id=supplier_id,
            change_type=change_type,
            rationale=rationale,
            actor_id=actor_id,
            resulting_supplier_count=resulting_count,
            requirement_tags="REQ-DOMAIN-008"
        )
        
        self.session.add(adjustment)
        self.session.flush()
        
        return {
            "adjustment_id": adjustment.id,
            "case_id": case_id,
            "supplier_id": supplier_id,
            "change_type": change_type,
            "rationale": rationale,
            "actor_id": actor_id,
            "resulting_supplier_count": resulting_count,
            "created_at": adjustment.created_at.isoformat()
        }
    
    def lock_longlist(
        self,
        case_id: int,
        actor_id: str
    ) -> dict[str, Any]:
        """
        Lock longlist before tender dispatch (ATS11).
        
        Creates immutable snapshot of finalized supplier set.
        Once locked, supplier set cannot be altered without unlock.
        
        Args:
            case_id: Case identifier
            actor_id: User ID performing lock
            
        Returns:
            Lock result dictionary with locked_longlist_id and locked suppliers
        """
        # Check if already locked
        existing_lock = self.lock_repo.get_locked_longlist_by_case(case_id)
        if existing_lock:
            raise ValueError(f"Case {case_id} is already locked")
        
        # Get latest proposal
        proposals = self.longlist_repo.list_case_proposals(case_id)
        if not proposals:
            raise ValueError(f"No longlist proposal found for case {case_id}")
        proposal = proposals[0]
        
        # Get proposal suppliers
        proposal_suppliers = self.longlist_repo.get_proposal_suppliers(proposal.id)
        if not proposal_suppliers:
            raise ValueError(f"No suppliers in proposal for case {case_id}")
        
        # Create locked longlist record
        locked_longlist = self.lock_repo.create_locked_longlist(
            case_id=case_id,
            source_proposal_id=proposal.id,
            lock_status="locked",
            locked_by=actor_id,
            requirement_tags="REQ-DOMAIN-010"
        )
        
        # Create locked supplier snapshot
        locked_suppliers = []
        for ps in proposal_suppliers:
            locked_supplier = self.lock_repo.create_locked_supplier(
                locked_longlist_id=locked_longlist.id,
                supplier_id=ps.supplier_id,
                final_rank_position=ps.rank_position,
                requirement_tags="REQ-DOMAIN-010"
            )
            locked_suppliers.append({
                "locked_supplier_id": locked_supplier.id,
                "supplier_id": locked_supplier.supplier_id,
                "final_rank_position": locked_supplier.final_rank_position
            })
        
        self.session.flush()
        
        return {
            "locked_longlist_id": locked_longlist.id,
            "case_id": case_id,
            "source_proposal_id": proposal.id,
            "lock_status": locked_longlist.lock_status,
            "locked_by": locked_longlist.locked_by,
            "locked_at": locked_longlist.locked_at.isoformat(),
            "locked_suppliers": locked_suppliers,
            "total_suppliers": len(locked_suppliers)
        }
    
    def dispatch_tender(
        self,
        case_id: int,
        actor_id: str
    ) -> dict[str, Any]:
        """
        Dispatch tender to finalized suppliers (ATS12).
        
        Invokes TOL6 adapter to distribute tender to each supplier
        on the locked longlist. Records per-supplier delivery outcomes.
        
        Args:
            case_id: Case identifier
            actor_id: User ID performing dispatch
            
        Returns:
            Dispatch result dictionary with batch reference and recipients
        """
        # Get locked longlist
        locked_longlist = self.lock_repo.get_locked_longlist_by_case(case_id)
        if not locked_longlist:
            raise ValueError(f"Case {case_id} must be locked before dispatch")
        
        # Check if already dispatched
        existing_dispatch = self.dispatch_repo.get_tender_dispatch_by_locked_longlist(
            locked_longlist.id
        )
        if existing_dispatch:
            raise ValueError(f"Case {case_id} has already been dispatched")
        
        # Get locked suppliers
        locked_suppliers = self.lock_repo.list_locked_suppliers(locked_longlist.id)
        if not locked_suppliers:
            raise ValueError(f"No locked suppliers found for case {case_id}")
        
        # Prepare supplier data for TOL6 adapter
        supplier_data = [
            {
                "supplier_id": ls.supplier_id,
                "rank_position": ls.final_rank_position
            }
            for ls in locked_suppliers
        ]
        
        # Generate dispatch batch reference
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        dispatch_batch_ref = f"BATCH-{case_id}-{timestamp}"
        
        # Invoke TOL6 adapter
        dispatch_result = self.tol6_adapter.dispatch_tender(
            case_id=case_id,
            locked_suppliers=supplier_data,
            dispatch_batch_ref=dispatch_batch_ref
        )
        
        # Create tender dispatch record
        tender_dispatch = self.dispatch_repo.create_tender_dispatch(
            locked_longlist_id=locked_longlist.id,
            dispatch_batch_ref=dispatch_result["dispatch_batch_ref"],
            dispatch_status=dispatch_result["dispatch_status"],
            dispatched_by=actor_id,
            requirement_tags="REQ-INT-004"
        )
        
        # Create dispatch recipient records
        recipients = []
        for recipient_data in dispatch_result["recipients"]:
            recipient = self.dispatch_repo.create_dispatch_recipient(
                dispatch_id=tender_dispatch.id,
                supplier_id=recipient_data["supplier_id"],
                delivery_status=recipient_data["delivery_status"],
                external_delivery_ref=recipient_data.get("external_delivery_ref"),
                requirement_tags="REQ-INT-004"
            )
            recipients.append({
                "recipient_id": recipient.id,
                "supplier_id": recipient.supplier_id,
                "delivery_status": recipient.delivery_status,
                "external_delivery_ref": recipient.external_delivery_ref
            })
        
        self.session.flush()
        
        return {
            "dispatch_id": tender_dispatch.id,
            "dispatch_batch_ref": tender_dispatch.dispatch_batch_ref,
            "dispatch_status": tender_dispatch.dispatch_status,
            "dispatched_by": tender_dispatch.dispatched_by,
            "dispatched_at": tender_dispatch.dispatched_at.isoformat(),
            "recipients": recipients,
            "total_recipients": len(recipients)
        }
