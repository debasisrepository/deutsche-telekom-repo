"""Service for longlist lock operations (ATS11)."""

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.adapters.tol4_validation_util import TOL4ValidationUtil
from app.models.audit_event import AuditEvent
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.longlist_repository import LonglistRepository
from app.repositories.need_repository import NeedRepository

logger = logging.getLogger(__name__)


class LonglistLockService:
    """
    Service for finalizing and locking longlist records (ATS11).

    ATS11 accepts longlist_id, expected_validation_verdict (must be pass),
    supplier_ids, finalized_by; executes single transaction: revalidate
    current set, persist immutable Longlist with locked=true/change_history/
    validation_verdict/validation_count, write audit event, mark workflow locked;
    returns longlist_id, need_id, suppliers, locked, locked_at. Commit fails
    if validation_verdict not pass.
    """

    def __init__(self, session: Session):
        self.session = session
        self.longlist_repo = LonglistRepository(session)
        self.need_repo = NeedRepository(session)
        self.audit_repo = AuditEventRepository(session)
        self.validation_util = TOL4ValidationUtil()

    def lock_by_id(
        self,
        id: UUID,
        expected_validation_verdict: str,
        supplier_ids: List[str],
        finalized_by: str,
        correlation_id: str,
    ) -> dict:
        """
        Lock a longlist by either proposal_id or longlist_id (ATS11).

        Automatically detects whether the ID is a proposal or longlist and
        routes to the appropriate method.

        Args:
            id: Either a proposal_id or longlist_id
            expected_validation_verdict: Must be "pass"
            supplier_ids: Final supplier IDs to lock
            finalized_by: User who finalized the longlist
            correlation_id: Correlation ID for audit trail

        Returns:
            Dict with longlist_id, need_id, suppliers, locked, locked_at,
            change_history, validation_count

        Raises:
            HTTPException: If neither proposal nor longlist found, or validation fails
        """
        from app.models.longlist import Longlist
        from app.models.longlist_proposal import LonglistProposal

        # First check if it's a longlist_id
        longlist = self.session.query(Longlist).filter(Longlist.id == id).first()
        if longlist:
            return self.lock_longlist(
                longlist_id=id,
                expected_validation_verdict=expected_validation_verdict,
                supplier_ids=supplier_ids,
                finalized_by=finalized_by,
                correlation_id=correlation_id,
            )

        # Otherwise check if it's a proposal_id
        proposal = self.session.query(LonglistProposal).filter(
            LonglistProposal.id == id
        ).first()
        if proposal:
            return self.lock_longlist_from_proposal(
                proposal_id=id,
                expected_validation_verdict=expected_validation_verdict,
                supplier_ids=supplier_ids,
                finalized_by=finalized_by,
                correlation_id=correlation_id,
            )

        # Neither found
        logger.error(f"No longlist or proposal found with ID {id}")
        raise HTTPException(
            status_code=404,
            detail=f"No longlist or proposal found with ID {id}"
        )

    def lock_longlist_from_proposal(
        self,
        proposal_id: UUID,
        expected_validation_verdict: str,
        supplier_ids: List[str],
        finalized_by: str,
        correlation_id: str,
    ) -> dict:
        """
        Create and lock a longlist from a proposal (ATS11).

        Finds or creates a longlist record for the given proposal, then locks it.

        Args:
            proposal_id: Proposal ID to create longlist from
            expected_validation_verdict: Must be "pass"
            supplier_ids: Final supplier IDs to lock
            finalized_by: User who finalized the longlist
            correlation_id: Correlation ID for audit trail

        Returns:
            Dict with longlist_id, need_id, suppliers, locked, locked_at,
            change_history, validation_count

        Raises:
            HTTPException: If proposal not found or validation fails
        """
        from app.models.longlist import Longlist
        from app.models.longlist_proposal import LonglistProposal

        # Get the proposal
        proposal = self.session.query(LonglistProposal).filter(
            LonglistProposal.id == proposal_id
        ).first()
        if not proposal:
            logger.error(f"Proposal {proposal_id} not found")
            raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")

        # Check if longlist already exists for this proposal
        existing_longlist = self.session.query(Longlist).filter(
            Longlist.proposal_id == proposal_id
        ).first()

        if existing_longlist:
            # Use existing longlist
            longlist_id = existing_longlist.id
        else:
            # Create new longlist
            longlist = Longlist(
                id=uuid.uuid4(),
                need_id=proposal.need_id,
                proposal_id=proposal_id,
                suppliers=json.dumps(supplier_ids),
                locked=False,
                change_history=json.dumps([]),
            )
            self.session.add(longlist)
            self.session.flush()
            longlist_id = longlist.id

        # Now lock it using the existing lock_longlist method
        return self.lock_longlist(
            longlist_id=longlist_id,
            expected_validation_verdict=expected_validation_verdict,
            supplier_ids=supplier_ids,
            finalized_by=finalized_by,
            correlation_id=correlation_id,
        )

    def lock_longlist(
        self,
        longlist_id: UUID,
        expected_validation_verdict: str,
        supplier_ids: List[str],
        finalized_by: str,
        correlation_id: str,
    ) -> dict:
        """
        Finalize and lock a longlist immutably (ATS11).

        Args:
            longlist_id: Longlist ID to lock
            expected_validation_verdict: Must be "pass"
            supplier_ids: Final supplier IDs to lock
            finalized_by: User who finalized the longlist
            correlation_id: Correlation ID for audit trail

        Returns:
            Dict with longlist_id, need_id, suppliers, locked, locked_at,
            change_history, validation_count

        Raises:
            HTTPException: If longlist not found, already locked, or
                          validation fails
        """
        # Verify expected_validation_verdict is "pass"
        if expected_validation_verdict != "pass":
            logger.error(
                f"Lock rejected for longlist {longlist_id}: "
                f"expected_validation_verdict must be 'pass', got '{expected_validation_verdict}'"
            )
            raise HTTPException(
                status_code=400,
                detail=f"expected_validation_verdict must be 'pass', got '{expected_validation_verdict}'",
            )

        # Retrieve longlist
        longlist = self.longlist_repo.get_by_id(longlist_id)
        if not longlist:
            logger.error(f"Longlist {longlist_id} not found")
            raise HTTPException(status_code=404, detail=f"Longlist {longlist_id} not found")

        # Check if already locked
        if longlist.locked:
            logger.error(f"Longlist {longlist_id} is already locked")
            raise HTTPException(
                status_code=400,
                detail=f"Longlist {longlist_id} is already locked and immutable",
            )

        # Revalidate current supplier set using TOL4
        validation_result = self.validation_util.validate_supplier_count(len(supplier_ids))

        if validation_result["verdict"] != "pass":
            # Log audit event for failed lock attempt
            audit_event = AuditEvent(
                id=uuid.uuid4(),
                need_id=longlist.need_id,
                correlation_id=correlation_id,
                step_code="ATS11",
                agent_code="AGN3",
                tool_code="TOL4",
                actor_type="human",
                actor_id=finalized_by,
                outcome="lock_rejected_validation_failed",
                severity="warning",
                payload_ref=json.dumps({
                    "longlist_id": str(longlist_id),
                    "validation_verdict": validation_result["verdict"],
                    "violations": validation_result["violations"],
                    "supplier_count": len(supplier_ids),
                }),
            )
            self.audit_repo.create(audit_event)

            logger.error(
                f"Lock rejected for longlist {longlist_id}: validation failed with verdict '{validation_result['verdict']}'"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Lock rejected: validation verdict is '{validation_result['verdict']}', expected 'pass'. "
                       f"Violations: {', '.join(validation_result['violations'])}",
            )

        # Parse existing change_history
        try:
            change_history = json.loads(longlist.change_history) if longlist.change_history else []
        except json.JSONDecodeError:
            change_history = []

        # Update longlist to locked state (immutable)
        longlist.locked = True
        longlist.locked_at = datetime.now(UTC)
        longlist.locked_by = finalized_by
        longlist.suppliers = json.dumps(supplier_ids)
        longlist.validation_verdict_at_lock = validation_result["verdict"]

        # Update change_history with lock event (for transparency)
        change_history.append({
            "action": "lock",
            "timestamp": longlist.locked_at.isoformat(),
            "actor": finalized_by,
            "supplier_ids": supplier_ids,
            "validation_verdict": validation_result["verdict"],
        })
        longlist.change_history = json.dumps(change_history)

        # Commit longlist changes
        self.longlist_repo.update(longlist)

        # Write audit event for successful lock
        audit_event = AuditEvent(
            id=uuid.uuid4(),
            need_id=longlist.need_id,
            correlation_id=correlation_id,
            step_code="ATS11",
            agent_code="AGN3",
            tool_code="TOL4",
            actor_type="human",
            actor_id=finalized_by,
            outcome="longlist_locked",
            severity="info",
            payload_ref=json.dumps({
                "longlist_id": str(longlist_id),
                "need_id": str(longlist.need_id),
                "supplier_count": len(supplier_ids),
                "validation_verdict": validation_result["verdict"],
                "locked_at": longlist.locked_at.isoformat(),
            }),
        )
        self.audit_repo.create(audit_event)

        logger.info(
            f"Longlist {longlist_id} locked successfully by {finalized_by} "
            f"with {len(supplier_ids)} suppliers"
        )

        return {
            "longlist_id": longlist.id,
            "need_id": longlist.need_id,
            "suppliers": supplier_ids,
            "locked": longlist.locked,
            "locked_at": longlist.locked_at,
            "change_history": change_history,
            "validation_count": len(supplier_ids),
            "correlation_id": correlation_id,
        }
