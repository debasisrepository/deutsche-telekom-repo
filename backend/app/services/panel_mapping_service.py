"""Panel Mapping Service - ATS6 implementation.

Maps classified needs to pre-selection panels and functional groups,
detecting coverage gaps that trigger niche research (ATS7).
"""

import uuid
from uuid import UUID

from sqlalchemy.orm import Session

from app.adapters.tol3_panel_adapter import TOL3PanelAdapter
from app.models.audit_event import AuditEvent
from app.models.panel_match import PanelMatch
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.need_repository import NeedRepository
from app.repositories.panel_match_repository import PanelMatchRepository
from app.schemas.panel_schemas import CandidateSupplier, PanelMappingResponse


class PanelMappingService:
    """Service for ATS6 panel and functional-group mapping."""

    def __init__(self, db: Session):
        self.db = db
        self.need_repo = NeedRepository(db)
        self.panel_match_repo = PanelMatchRepository(db)
        self.audit_repo = AuditEventRepository(db)
        self.tol3_adapter = TOL3PanelAdapter()

    def map_need_to_panels(
        self,
        need_id: UUID,
        need_category: str,
        correlation_id: str,
    ) -> PanelMappingResponse:
        """Execute ATS6 panel mapping.

        Args:
            need_id: UUID of the need to map
            need_category: Category for panel matching
            correlation_id: Request correlation ID

        Returns:
            PanelMappingResponse with candidate suppliers and coverage gap flag

        Raises:
            ValueError: If need not found or not in correct state
        """
        # Validate need exists
        need = self.need_repo.get_by_id(need_id)
        if not need:
            raise ValueError(f"Need {need_id} not found")

        # Query TOL3 panel catalog
        catalog_result = self.tol3_adapter.query_panel_catalog(
            need_id=need_id,
            need_category=need_category,
        )

        candidate_suppliers_data = catalog_result.get("candidate_suppliers", [])
        coverage_gap_flag = catalog_result.get("coverage_gap_flag", False)

        # Create PanelMatch records for each candidate
        panel_matches = []
        for supplier_data in candidate_suppliers_data:
            panel_match = PanelMatch(
                id=uuid.uuid4(),
                need_id=need_id,
                supplier_id=supplier_data["supplier_id"],
                panel_source=supplier_data["panel_source"],
                functional_group=supplier_data["functional_group"],
                provenance_ref=supplier_data["provenance_ref"],
                coverage_gap_flag=coverage_gap_flag,
            )
            panel_matches.append(panel_match)

        # Persist panel matches
        if panel_matches:
            self.panel_match_repo.create_batch(panel_matches)

        # Write audit event for ATS6
        audit_event = AuditEvent(
            need_id=need_id,
            correlation_id=correlation_id,
            step_code="ATS6",
            agent_code="AGN2",
            tool_code="TOL3",
            actor_type="system",
            actor_id="panel_mapping_service",
            outcome="mapped" if not coverage_gap_flag else "coverage_gap_detected",
            severity="info",
            payload_ref=f"Panel mapping for need {need_id}: {len(panel_matches)} candidates, gap={coverage_gap_flag}",
        )
        self.audit_repo.create(audit_event)

        # Build response
        candidate_suppliers = [
            CandidateSupplier(
                panel_match_id=pm.id,
                supplier_id=pm.supplier_id,
                panel_source=pm.panel_source,
                functional_group=pm.functional_group,
                provenance_ref=pm.provenance_ref,
            )
            for pm in panel_matches
        ]

        return PanelMappingResponse(
            need_id=need_id,
            candidate_suppliers=candidate_suppliers,
            coverage_gap_flag=coverage_gap_flag,
            correlation_id=correlation_id,
        )
