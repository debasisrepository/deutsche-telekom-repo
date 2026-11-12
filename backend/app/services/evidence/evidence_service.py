"""Evidence Service - Evidence retrieval and citation management."""
from typing import Any

from sqlalchemy.orm import Session

from app.adapters.tol2_supplier_kb_adapter import TOL2SupplierKBAdapter
from app.models.case_evidence import CaseEvidence
from app.repositories.evidence_repository import EvidenceRepository


class EvidenceService:
    """Service for managing historical supplier evidence."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = EvidenceRepository(session)
        self.tol2_adapter = TOL2SupplierKBAdapter()

    def store_evidence(
        self,
        case_id: int,
        need_attributes: dict[str, Any],
        requirement_tags: str | None = None
    ) -> list[CaseEvidence]:
        """Retrieve and store evidence for a case.
        
        Queries TOL2 adapter for historical evidence, normalizes results,
        creates or links suppliers, historical orders, and SoWs, and stores
        case evidence records.
        
        Args:
            case_id: Case identifier
            need_attributes: Extracted need attributes for evidence matching
            requirement_tags: Optional requirement tags
            
        Returns:
            List of created CaseEvidence instances
        """
        # Query TOL2 adapter for historical evidence
        raw_evidence = self.tol2_adapter.query_historical_evidence(case_id, need_attributes)

        evidence_records = []
        for item in raw_evidence:
            # Get or create supplier
            supplier = self.repository.get_or_create_supplier(
                supplier_code=item["supplier_code"],
                display_name=item["supplier_name"],
                status="active"
            )

            # Link historical order or commissioned SoW if present
            historical_order_id = None
            commissioned_sow_id = None

            if item.get("evidence_type") == "historical_order":
                order = self.repository.get_or_create_historical_order(
                    external_order_id=item["external_ref"],
                    service_domain=item.get("service_domain", ""),
                    completion_date=item.get("completion_date", "2025-01-01")
                )
                historical_order_id = order.id
            elif item.get("evidence_type") == "commissioned_sow":
                sow = self.repository.get_or_create_commissioned_sow(
                    external_sow_id=item["external_ref"],
                    scope_summary=item.get("evidence_summary", ""),
                    signed_date=item.get("signed_date", "2025-01-01")
                )
                commissioned_sow_id = sow.id

            # Create case evidence record
            evidence = self.repository.create_case_evidence(
                case_id=case_id,
                supplier_id=supplier.id,
                citation_label=item["citation_label"],
                citation_ref=item["citation_ref"],
                evidence_summary=item["evidence_summary"],
                evidence_found=item.get("evidence_found", True),
                historical_order_id=historical_order_id,
                commissioned_sow_id=commissioned_sow_id,
                requirement_tags=requirement_tags
            )
            evidence_records.append(evidence)

        self.session.commit()
        return evidence_records

    def list_evidence(self, case_id: int) -> list[dict[str, Any]]:
        """List evidence for a case with supplier details.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of evidence dictionaries with supplier and citation details
        """
        evidence_records = self.repository.list_case_evidence(case_id)

        results = []
        for evidence in evidence_records:
            supplier = self.repository.get_supplier_by_id(evidence.supplier_id) if evidence.supplier_id else None

            results.append({
                "id": evidence.id,
                "case_id": evidence.case_id,
                "supplier": {
                    "id": supplier.id if supplier else None,
                    "supplier_code": supplier.supplier_code if supplier else None,
                    "display_name": supplier.display_name if supplier else None,
                    "status": supplier.status if supplier else None
                } if supplier else None,
                "citation_label": evidence.citation_label,
                "citation_ref": evidence.citation_ref,
                "evidence_summary": evidence.evidence_summary,
                "evidence_found": evidence.evidence_found,
                "created_at": evidence.created_at.isoformat() if evidence.created_at else None
            })

        return results
