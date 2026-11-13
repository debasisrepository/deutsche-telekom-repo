"""TOL5 VMS adapter for single-resource handoff."""
import uuid
from datetime import UTC, datetime


class TOL5VmsAdapter:
    """
    TOL5 VMS connector for single-resource handoff.

    Integrates with VMS (Vendor Management System) for single-resource
    procurement handoff. For local development without external VMS API,
    generates valid VMS reference IDs and simulates successful handoff.
    """

    def send_handoff(self, need_id: uuid.UUID, request_payload: dict) -> dict:
        """
        Send single-resource need to VMS.

        Args:
            need_id: The need identifier
            request_payload: Normalized need record for VMS

        Returns:
            dict with handover_confirmation, vms_reference_id, response_payload_json
        """
        # Execute VMS handoff - generate VMS reference ID
        # In production environment with VMS API access, this would make HTTP request
        # For local development, generate valid reference following VMS format
        vms_ref = f"VMS-{datetime.now(UTC).strftime('%Y')}-{str(uuid.uuid4())[:6].upper()}"

        return {
            "handover_confirmation": True,
            "vms_reference_id": vms_ref,
            "response_payload_json": {
                "status": "accepted",
                "vms_ticket_id": vms_ref,
                "received_at": datetime.now(UTC).isoformat(),
                "estimated_processing_time": "2-3 business days",
            },
            "error_detail": None,
        }

    def send_handoff_with_failure(self, need_id: uuid.UUID, request_payload: dict, simulate_failure: bool = False) -> dict:
        """
        Send handoff with optional failure simulation for testing.

        Args:
            need_id: The need identifier
            request_payload: Normalized need record for VMS
            simulate_failure: If True, simulate a VMS connection failure

        Returns:
            dict with handover_confirmation, error_detail
        """
        if simulate_failure:
            return {
                "handover_confirmation": False,
                "vms_reference_id": None,
                "response_payload_json": None,
                "error_detail": "VMS connection timeout - escalation required",
            }

        return self.send_handoff(need_id, request_payload)
