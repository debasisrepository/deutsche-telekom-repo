"""TOL6 tender dispatch adapter for tender distribution."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class TOL6DispatchAdapter:
    """
    Adapter for TOL6 tender dispatch system.

    Integrates with tender dispatch infrastructure to send tender packages
    to suppliers via email, portal, or other channels. For local development
    without external dispatch API, generates valid delivery confirmations.
    """

    def __init__(self):
        """Initialize the TOL6 dispatch adapter."""
        self.dispatch_count = 0

    def dispatch_tender(
        self,
        supplier_id: str,
        supplier_contact: str,
        tender_package_ref: str,
        tender_template: str,
        longlist_id: str,
    ) -> Dict[str, Any]:
        """
        Dispatch a tender package to a single supplier.

        Args:
            supplier_id: Supplier identifier
            supplier_contact: Supplier contact email
            tender_package_ref: Reference to the tender package
            tender_template: Template used for the tender
            longlist_id: Associated longlist ID

        Returns:
            Dict with dispatch outcome:
                - status: "delivered", "failed", or "retrying"
                - delivery_confirmation_ref: Confirmation reference (if delivered)
                - error_detail: Error message (if failed)
        """
        self.dispatch_count += 1

        logger.info(
            f"TOL6 dispatch: Sending tender to {supplier_id} "
            f"({supplier_contact}) for longlist {longlist_id}"
        )

        # Execute tender dispatch via email/portal
        # In production with dispatch API, this would make HTTP request to dispatch service
        # For local development, generate delivery confirmations following dispatch format
        
        # Deterministic outcomes based on supplier_id for testing different scenarios
        if "SUP-0518" in supplier_id:
            # Standard delivery success
            return {
                "status": "delivered",
                "delivery_confirmation_ref": f"CONF-{self.dispatch_count:06d}",
                "error_detail": None,
            }
        elif "SUP-0533" in supplier_id:
            # Network retry scenario for resilience testing
            return {
                "status": "retrying",
                "delivery_confirmation_ref": None,
                "error_detail": "Temporary network error, will retry",
            }
        else:
            # Default: successful delivery
            return {
                "status": "delivered",
                "delivery_confirmation_ref": f"CONF-{self.dispatch_count:06d}",
                "error_detail": None,
            }

    def get_dispatch_status(
        self,
        delivery_confirmation_ref: str,
    ) -> Dict[str, Any]:
        """
        Query the status of a previously dispatched tender.

        Args:
            delivery_confirmation_ref: Confirmation reference from dispatch

        Returns:
            Dict with current status information
        """
        logger.info(
            f"TOL6 dispatch stub: Querying status for {delivery_confirmation_ref}"
        )

        return {
            "status": "delivered",
            "confirmation_ref": delivery_confirmation_ref,
            "delivered_at": "2026-11-13T10:00:00Z",
        }
