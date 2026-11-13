import uuid
from datetime import UTC, datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.adapters.tol2_evidence_adapter import TOL2EvidenceAdapter
from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.evidence_schemas import EvidenceItem, EvidenceQueryResponse


class SupplierEvidenceService:
    """
    Service for ATS5: Retrieve historical supplier and project evidence.

    Queries TOL2 for evidence and gracefully degrades to seed data when unavailable.
    Never fabricates suppliers, SoWs, or performance history.
    """

    def __init__(self, session: Session):
        self.session = session
        self.evidence_repo = EvidenceRepository(session)
        self.tol2_adapter = TOL2EvidenceAdapter()

    def query_evidence(
        self,
        need_id: str,
        service_type: Optional[str] = None,
        required_skills: Optional[List[str]] = None,
        business_unit_id: Optional[str] = None,
        panel_filters: Optional[List[str]] = None,
        correlation_id: Optional[str] = None,
    ) -> EvidenceQueryResponse:
        """
        Query historical supplier evidence for a need (ATS5).

        Returns evidence from TOL2 when available, falls back to seed data otherwise.
        Sets evidence_limited_flag when using fallback.
        """
        need_uuid = uuid.UUID(need_id)
        snapshot_timestamp = datetime.now(UTC)

        tol2_result = self.tol2_adapter.query_evidence(
            need_id=need_uuid,
            service_type=service_type,
            required_skills=required_skills,
            business_unit_id=business_unit_id,
            panel_filters=panel_filters,
        )

        evidence_limited_flag = not tol2_result["available"]

        if tol2_result["available"] and len(tol2_result["evidence_items"]) > 0:
            evidence_items = self._convert_tol2_items(tol2_result["evidence_items"])
            snapshot_timestamp = tol2_result["snapshot_timestamp"]
        else:
            evidence_items = self._get_seed_evidence(need_uuid)
            evidence_limited_flag = True

        return EvidenceQueryResponse(
            evidence_items=evidence_items,
            evidence_limited_flag=evidence_limited_flag,
            evidence_snapshot_timestamp=snapshot_timestamp,
            correlation_id=correlation_id,
        )

    def _convert_tol2_items(self, tol2_items: List[dict]) -> List[EvidenceItem]:
        """Convert TOL2 evidence items to schema format."""
        converted = []
        for item in tol2_items:
            converted.append(
                EvidenceItem(
                    supplier_id=item.get("supplier_id", ""),
                    evidence_type=item.get("evidence_type", ""),
                    source_system=item.get("source_system", "TOL2"),
                    source_reference=item.get("source_reference", ""),
                    service_category=item.get("service_category", ""),
                    business_unit=item.get("business_unit"),
                    delivery_period=item.get("delivery_period"),
                    quality_rating=item.get("quality_rating"),
                    citation_text=item.get("citation_text", ""),
                    is_seed_data=False,
                    snapshot_timestamp=item.get("snapshot_timestamp", datetime.now(UTC)),
                )
            )
        return converted

    def _get_seed_evidence(self, need_id: uuid.UUID) -> List[EvidenceItem]:
        """
        Retrieve seed evidence items for graceful degradation.

        Returns existing seed evidence for the need, or empty list if none exists.
        Never fabricates suppliers or evidence when unavailable.
        """
        seed_items = self.evidence_repo.get_by_need_id(need_id)

        evidence_items = []
        for item in seed_items:
            evidence_items.append(
                EvidenceItem(
                    supplier_id=item.supplier_id,
                    evidence_type=item.evidence_type,
                    source_system=item.source_system,
                    source_reference=item.source_reference,
                    service_category=item.service_category,
                    business_unit=item.business_unit_id,
                    delivery_period=item.delivery_period,
                    quality_rating=item.quality_rating,
                    citation_text=item.citation_text,
                    is_seed_data=item.is_seed_data,
                    snapshot_timestamp=item.evidence_snapshot_timestamp,
                )
            )

        return evidence_items
