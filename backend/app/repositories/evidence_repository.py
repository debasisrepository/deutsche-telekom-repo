"""Evidence Repository - Data access for evidence records."""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.case_evidence import CaseEvidence
from app.models.commissioned_sow import CommissionedSoW
from app.models.historical_order import HistoricalOrder
from app.models.supplier import Supplier


class EvidenceRepository:
    """Repository for evidence-related data access."""

    def __init__(self, session: Session):
        self.session = session

    def get_or_create_supplier(self, supplier_code: str, display_name: str, status: str = "active") -> Supplier:
        """Get existing supplier or create new one.
        
        Args:
            supplier_code: Unique supplier identifier
            display_name: Supplier display name
            status: Supplier status (default: active)
            
        Returns:
            Supplier instance
        """
        supplier = self.session.query(Supplier).filter_by(supplier_code=supplier_code).first()
        if not supplier:
            supplier = Supplier(
                supplier_code=supplier_code,
                display_name=display_name,
                status=status,
                evidence_source_status="available"
            )
            self.session.add(supplier)
            self.session.flush()
        return supplier

    def get_or_create_historical_order(self, external_order_id: str, service_domain: str, completion_date: str) -> HistoricalOrder:
        """Get existing historical order or create new one.
        
        Args:
            external_order_id: External order reference
            service_domain: Service domain category
            completion_date: Order completion date (ISO format string)
            
        Returns:
            HistoricalOrder instance
        """
        order = self.session.query(HistoricalOrder).filter_by(external_order_id=external_order_id).first()
        if not order:
            # Parse ISO date string to date object
            date_obj = datetime.fromisoformat(completion_date).date() if isinstance(completion_date, str) else completion_date
            order = HistoricalOrder(
                external_order_id=external_order_id,
                service_domain=service_domain,
                completion_date=date_obj
            )
            self.session.add(order)
            self.session.flush()
        return order

    def get_or_create_commissioned_sow(self, external_sow_id: str, scope_summary: str, signed_date: str) -> CommissionedSoW:
        """Get existing commissioned SoW or create new one.
        
        Args:
            external_sow_id: External SoW reference
            scope_summary: Summary of SoW scope
            signed_date: SoW signing date (ISO format string)
            
        Returns:
            CommissionedSoW instance
        """
        sow = self.session.query(CommissionedSoW).filter_by(external_sow_id=external_sow_id).first()
        if not sow:
            # Parse ISO date string to date object
            date_obj = datetime.fromisoformat(signed_date).date() if isinstance(signed_date, str) else signed_date
            sow = CommissionedSoW(
                external_sow_id=external_sow_id,
                scope_summary=scope_summary,
                signed_date=date_obj
            )
            self.session.add(sow)
            self.session.flush()
        return sow

    def create_case_evidence(
        self,
        case_id: int,
        supplier_id: int,
        citation_label: str,
        citation_ref: str,
        evidence_summary: str,
        evidence_found: bool = True,
        historical_order_id: int | None = None,
        commissioned_sow_id: int | None = None,
        requirement_tags: str | None = None
    ) -> CaseEvidence:
        """Create case evidence record.
        
        Args:
            case_id: Case identifier
            supplier_id: Supplier identifier
            citation_label: Human-readable citation label
            citation_ref: Citation reference path
            evidence_summary: Evidence summary text
            evidence_found: Whether evidence was found (default: True)
            historical_order_id: Optional historical order link
            commissioned_sow_id: Optional commissioned SoW link
            requirement_tags: Optional requirement tags
            
        Returns:
            CaseEvidence instance
        """
        evidence = CaseEvidence(
            case_id=case_id,
            supplier_id=supplier_id,
            historical_order_id=historical_order_id,
            commissioned_sow_id=commissioned_sow_id,
            citation_label=citation_label,
            citation_ref=citation_ref,
            evidence_summary=evidence_summary,
            evidence_found=evidence_found,
            requirement_tags=requirement_tags
        )
        self.session.add(evidence)
        self.session.flush()
        return evidence

    def list_case_evidence(self, case_id: int) -> list[CaseEvidence]:
        """List all evidence records for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of CaseEvidence instances
        """
        return self.session.query(CaseEvidence).filter_by(case_id=case_id).all()

    def get_supplier_by_id(self, supplier_id: int) -> Supplier | None:
        """Get supplier by ID.
        
        Args:
            supplier_id: Supplier identifier
            
        Returns:
            Supplier instance or None
        """
        return self.session.query(Supplier).filter_by(id=supplier_id).first()
