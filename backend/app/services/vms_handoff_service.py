"""VMS handoff service for ATS4."""
import json
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.adapters.tol5_vms_adapter import TOL5VmsAdapter
from app.models.audit_event import AuditEvent
from app.models.vms_handoff import VmsHandoff
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.need_repository import NeedRepository
from app.repositories.vms_handoff_repository import VmsHandoffRepository
from app.schemas.vms_schemas import VmsHandoffRequest, VmsHandoffResponse, VmsHandoffListItem


class VmsHandoffService:
    """Service for ATS4 VMS handoff execution."""

    def __init__(self, session: Session):
        self.session = session
        self.need_repo = NeedRepository(session)
        self.handoff_repo = VmsHandoffRepository(session)
        self.audit_repo = AuditEventRepository(session)
        self.vms_adapter = TOL5VmsAdapter()

    def execute_handoff(
        self,
        request: VmsHandoffRequest,
    ) -> VmsHandoffResponse:
        """
        ATS4: Execute VMS handoff for reviewed single-resource cases.

        Calls TOL5 VMS adapter, records handover_confirmation and vms_reference_id,
        marks workflow status as vms_routed_terminal, blocks ATS5-ATS12 for this need.
        Failed handoff escalates with error status.
        """
        # Retrieve need
        need = self.need_repo.get_by_id(request.need_id)
        if not need:
            raise ValueError(f"Need {request.need_id} not found")

        # Enforce single_resource verdict requirement
        if request.classification_verdict != "single_resource":
            raise ValueError(
                f"VMS handoff only executes for single_resource verdict. "
                f"Got: {request.classification_verdict}"
            )

        # Verify need has been classified as single_resource
        if need.classification_verdict != "single_resource":
            raise ValueError(
                f"Need {request.need_id} classification_verdict is {need.classification_verdict}, "
                f"not single_resource. Cannot execute VMS handoff."
            )

        # Verify need is in correct workflow state
        if need.status != "classified_single_resource":
            raise ValueError(
                f"Need {request.need_id} status is {need.status}. "
                f"Expected classified_single_resource for VMS handoff."
            )

        # Prepare request payload
        request_payload = {
            "need_id": str(request.need_id),
            "classification_verdict": request.classification_verdict,
            **request.request_payload_json,
        }

        # Call TOL5 VMS adapter
        sent_at = datetime.now(UTC)
        try:
            vms_response = self.vms_adapter.send_handoff(request.need_id, request_payload)
        except Exception as e:
            # Failed handoff - record error and escalate
            vms_response = {
                "handover_confirmation": False,
                "vms_reference_id": None,
                "response_payload_json": None,
                "error_detail": f"VMS adapter error: {str(e)}",
            }

        # Create VMS handoff record
        handoff = VmsHandoff(
            id=uuid.uuid4(),
            need_id=request.need_id,
            handover_confirmation=vms_response["handover_confirmation"],
            vms_reference_id=vms_response.get("vms_reference_id"),
            workflow_status="vms_routed_terminal" if vms_response["handover_confirmation"] else "vms_handoff_failed",
            request_payload_json=json.dumps(request_payload),
            response_payload_json=json.dumps(vms_response.get("response_payload_json")) if vms_response.get("response_payload_json") else None,
            error_detail=vms_response.get("error_detail"),
        )
        self.handoff_repo.create(handoff)

        # Update need workflow status
        if vms_response["handover_confirmation"]:
            need.status = "vms_routed_terminal"
        else:
            need.status = "vms_handoff_failed"
        self.need_repo.update(need)

        # Write audit event
        audit_event = AuditEvent(
            id=uuid.uuid4(),
            need_id=request.need_id,
            correlation_id=need.correlation_id,
            step_code="ATS4",
            agent_code="AGN5",
            tool_code="TOL5",
            actor_type="system",
            actor_id="vms_handoff_service",
            outcome="success" if vms_response["handover_confirmation"] else "failed",
            severity="info" if vms_response["handover_confirmation"] else "error",
            payload_ref=(
                f"vms_ref={vms_response.get('vms_reference_id', 'none')}, "
                f"confirmation={vms_response['handover_confirmation']}"
            ),
        )
        self.audit_repo.create(audit_event)

        # Commit transaction
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return VmsHandoffResponse(
            vms_handoff_id=handoff.id,
            need_id=request.need_id,
            handover_confirmation=vms_response["handover_confirmation"],
            vms_reference_id=vms_response.get("vms_reference_id"),
            response_payload_json=vms_response.get("response_payload_json"),
            sent_at=sent_at,
            correlation_id=uuid.UUID(need.correlation_id),
            workflow_status=handoff.workflow_status,
        )

    def list_handoffs(self, limit: int = 100) -> list[VmsHandoffListItem]:
        """
        List all VMS handoffs with handoff status and workflow status.
        Returns handoffs ordered by created_at descending.
        """
        handoffs = self.handoff_repo.list_all(limit=limit)
        
        result = []
        for handoff in handoffs:
            need = self.need_repo.get_by_id(handoff.need_id)
            if need:
                result.append(
                    VmsHandoffListItem(
                        need_id=handoff.need_id,
                        classification_verdict=need.classification_verdict or "single_resource",
                        handover_confirmation=handoff.handover_confirmation,
                        vms_reference_id=handoff.vms_reference_id,
                        workflow_status=handoff.workflow_status,
                        created_at=handoff.created_at,
                    )
                )
        
        return result
