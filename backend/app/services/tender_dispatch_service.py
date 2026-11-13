"""Service for tender dispatch operations (ATS12)."""

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.adapters.tol6_dispatch_adapter import TOL6DispatchAdapter
from app.models.audit_event import AuditEvent
from app.models.tender_dispatch import TenderDispatch
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.longlist_repository import LonglistRepository
from app.repositories.tender_dispatch_repository import TenderDispatchRepository

logger = logging.getLogger(__name__)


class TenderDispatchService:
    """
    Service for tender dispatch operations (ATS12).

    ATS12 accepts longlist_id, tender_template, supplier_contacts array;
    blocks dispatch when longlist unlocked/empty/invalid contacts; builds
    tender package from locked longlist, dispatches to every supplier via TOL6,
    records per-supplier dispatch_status (pending|retrying|delivered|failed|
    escalated), retry_count, delivery_confirmation_ref, tender_package_ref,
    escalation_opened, last_attempt_at; returns dispatch_batch_id, longlist_id,
    supplier_dispatches array. Idempotent retry for failures, escalates after
    retry exhaustion.
    """

    MAX_RETRY_COUNT = 3

    def __init__(self, session: Session):
        self.session = session
        self.longlist_repo = LonglistRepository(session)
        self.dispatch_repo = TenderDispatchRepository(session)
        self.audit_repo = AuditEventRepository(session)
        self.tol6_adapter = TOL6DispatchAdapter()

    def dispatch_tender(
        self,
        longlist_id: UUID,
        tender_template: str,
        supplier_contacts: List[dict],
        correlation_id: str,
    ) -> dict:
        """
        Dispatch tender to all suppliers on locked longlist (ATS12).

        Args:
            longlist_id: Locked longlist ID
            tender_template: Tender template reference
            supplier_contacts: List of supplier contact information
            correlation_id: Correlation ID for audit trail

        Returns:
            Dict with dispatch_batch_id, longlist_id, supplier_dispatches array

        Raises:
            HTTPException: If longlist not found, not locked, empty, or
                          invalid contacts
        """
        # Retrieve longlist
        longlist = self.longlist_repo.get_by_id(longlist_id)
        if not longlist:
            logger.error(f"Longlist {longlist_id} not found")
            raise HTTPException(status_code=404, detail=f"Longlist {longlist_id} not found")

        # Block dispatch if longlist not locked
        if not longlist.locked:
            logger.error(f"Dispatch blocked for longlist {longlist_id}: not locked")
            raise HTTPException(
                status_code=400,
                detail=f"Dispatch blocked: longlist {longlist_id} is not locked",
            )

        # Parse suppliers from locked longlist
        try:
            suppliers = json.loads(longlist.suppliers) if isinstance(longlist.suppliers, str) else longlist.suppliers
        except json.JSONDecodeError:
            suppliers = []

        # Block dispatch if empty
        if not suppliers:
            logger.error(f"Dispatch blocked for longlist {longlist_id}: empty supplier list")
            raise HTTPException(
                status_code=400,
                detail=f"Dispatch blocked: longlist {longlist_id} has no suppliers",
            )

        # Validate supplier contacts
        if not supplier_contacts:
            logger.error(f"Dispatch blocked for longlist {longlist_id}: no supplier contacts provided")
            raise HTTPException(
                status_code=400,
                detail="Dispatch blocked: no supplier contacts provided",
            )

        # Create contact map for quick lookup
        contact_map = {contact["supplier_id"]: contact for contact in supplier_contacts}

        # Validate all suppliers have contacts
        missing_contacts = [s for s in suppliers if s not in contact_map]
        if missing_contacts:
            logger.error(
                f"Dispatch blocked for longlist {longlist_id}: "
                f"missing contacts for suppliers {missing_contacts}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Dispatch blocked: missing contacts for suppliers {', '.join(missing_contacts)}",
            )

        # Generate dispatch batch ID
        dispatch_batch_id = f"DSP-{datetime.now(UTC).strftime('%Y-%m-%d')}-{str(uuid.uuid4())[:8]}"

        # Dispatch to each supplier
        supplier_dispatches = []
        for supplier_id in suppliers:
            contact = contact_map[supplier_id]

            # Build tender package reference
            tender_package_ref = f"TND-{longlist_id}-{supplier_id}-{uuid.uuid4().hex[:8]}"

            # Call TOL6 adapter to dispatch
            try:
                dispatch_result = self.tol6_adapter.dispatch_tender(
                    supplier_id=supplier_id,
                    supplier_contact=contact["contact_email"],
                    tender_package_ref=tender_package_ref,
                    tender_template=tender_template,
                    longlist_id=str(longlist_id),
                )

                dispatch_status = dispatch_result["status"]
                delivery_confirmation_ref = dispatch_result.get("delivery_confirmation_ref")
                error_detail = dispatch_result.get("error_detail")

                # Determine retry count and escalation based on status
                retry_count = 0 if dispatch_status == "delivered" else 1
                escalation_opened = False

            except Exception as e:
                logger.error(f"TOL6 dispatch failed for supplier {supplier_id}: {e}")
                dispatch_status = "failed"
                delivery_confirmation_ref = None
                error_detail = str(e)
                retry_count = 1
                escalation_opened = False

            # Create tender dispatch record
            dispatch = TenderDispatch(
                id=uuid.uuid4(),
                longlist_id=longlist_id,
                dispatch_batch_id=dispatch_batch_id,
                supplier_id=supplier_id,
                supplier_contact=contact["contact_email"],
                dispatch_status=dispatch_status,
                retry_count=retry_count,
                delivery_confirmation_ref=delivery_confirmation_ref,
                error_detail=error_detail,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )

            self.dispatch_repo.create(dispatch)

            supplier_dispatches.append({
                "dispatch_id": dispatch.id,
                "supplier_id": supplier_id,
                "tender_package_ref": tender_package_ref,
                "dispatch_status": dispatch_status,
                "retry_count": retry_count,
                "delivery_confirmation_ref": delivery_confirmation_ref,
                "escalation_opened": escalation_opened,
                "last_attempt_at": dispatch.created_at,
            })

        # Write audit event for dispatch
        audit_event = AuditEvent(
            id=uuid.uuid4(),
            need_id=longlist.need_id,
            correlation_id=correlation_id,
            step_code="ATS12",
            agent_code="AGN3",
            tool_code="TOL6",
            actor_type="system",
            actor_id="tender_dispatch_service",
            outcome="tender_dispatched",
            severity="info",
            payload_ref=json.dumps({
                "dispatch_batch_id": dispatch_batch_id,
                "longlist_id": str(longlist_id),
                "supplier_count": len(suppliers),
                "tender_template": tender_template,
            }),
        )
        self.audit_repo.create(audit_event)

        logger.info(
            f"Tender dispatch batch {dispatch_batch_id} created for longlist {longlist_id} "
            f"with {len(suppliers)} suppliers"
        )

        return {
            "dispatch_batch_id": dispatch_batch_id,
            "longlist_id": longlist_id,
            "supplier_dispatches": supplier_dispatches,
            "correlation_id": correlation_id,
        }

    def retry_failed_dispatch(
        self,
        dispatch_id: UUID,
        correlation_id: str,
    ) -> dict:
        """
        Retry a failed dispatch (idempotent).

        Args:
            dispatch_id: Dispatch ID to retry
            correlation_id: Correlation ID for audit trail

        Returns:
            Dict with updated dispatch status

        Raises:
            HTTPException: If dispatch not found or already succeeded
        """
        dispatch = self.dispatch_repo.get_by_id(dispatch_id)
        if not dispatch:
            raise HTTPException(status_code=404, detail=f"Dispatch {dispatch_id} not found")

        if dispatch.dispatch_status == "delivered":
            logger.info(f"Dispatch {dispatch_id} already delivered, skipping retry")
            return {
                "dispatch_id": dispatch_id,
                "dispatch_status": dispatch.dispatch_status,
                "retry_count": dispatch.retry_count,
            }

        # Increment retry count
        dispatch.retry_count += 1

        # Escalate if retry exhausted
        if dispatch.retry_count > self.MAX_RETRY_COUNT:
            dispatch.dispatch_status = "escalated"
            dispatch.error_detail = f"Retry exhausted after {self.MAX_RETRY_COUNT} attempts"
            logger.warning(f"Dispatch {dispatch_id} escalated after {self.MAX_RETRY_COUNT} retries")
        else:
            # Attempt retry via TOL6
            try:
                self.longlist_repo.get_by_id(dispatch.longlist_id)
                tender_package_ref = f"TND-{dispatch.longlist_id}-{dispatch.supplier_id}-{uuid.uuid4().hex[:8]}"

                dispatch_result = self.tol6_adapter.dispatch_tender(
                    supplier_id=dispatch.supplier_id,
                    supplier_contact=dispatch.supplier_contact or "",
                    tender_package_ref=tender_package_ref,
                    tender_template="retry",
                    longlist_id=str(dispatch.longlist_id),
                )

                dispatch.dispatch_status = str(dispatch_result["status"])
                delivery_conf = dispatch_result.get("delivery_confirmation_ref")
                dispatch.delivery_confirmation_ref = str(delivery_conf) if delivery_conf else None
                error = dispatch_result.get("error_detail")
                dispatch.error_detail = str(error) if error else None

            except Exception as e:
                logger.error(f"Retry failed for dispatch {dispatch_id}: {e}")
                dispatch.dispatch_status = "failed"
                dispatch.error_detail = str(e)

        dispatch.updated_at = datetime.now(UTC)
        self.dispatch_repo.update(dispatch)

        logger.info(
            f"Dispatch {dispatch_id} retry attempt {dispatch.retry_count}, "
            f"status: {dispatch.dispatch_status}"
        )

        return {
            "dispatch_id": dispatch_id,
            "dispatch_status": dispatch.dispatch_status,
            "retry_count": dispatch.retry_count,
            "escalation_opened": dispatch.dispatch_status == "escalated",
        }
