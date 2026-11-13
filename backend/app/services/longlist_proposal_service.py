"""Longlist Proposal Service - ATS8 implementation.

Generates ranked longlist proposals with citation enforcement, evidence-based
supplier ranking, and reviewer workflow support.
"""

import json
import uuid
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.models.longlist_proposal import LonglistProposal
from app.models.longlist_ranked_supplier import LonglistRankedSupplier
from app.models.panel_match import PanelMatch
from app.models.provider_candidate import ProviderCandidate
from app.models.supplier_evidence_item import SupplierEvidenceItem
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.longlist_proposal_repository import LonglistProposalRepository
from app.repositories.need_repository import NeedRepository
from app.schemas.proposal_schemas import (
    EvidenceCitation,
    LonglistProposalResponse,
    RankedSupplierResponse,
)


class LonglistProposalService:
    """Service for ATS8 longlist proposal generation."""

    def __init__(self, db: Session):
        self.db = db
        self.need_repo = NeedRepository(db)
        self.proposal_repo = LonglistProposalRepository(db)
        self.audit_repo = AuditEventRepository(db)

    def generate_proposal(
        self,
        need_id: UUID,
        matched_panels: List[str],
        evidence_items: List[str],
        approved_niche_candidates: List[str],
        correlation_id: str,
    ) -> LonglistProposalResponse:
        """Generate ranked longlist proposal (ATS8).

        Args:
            need_id: UUID of the need
            matched_panels: List of panel match IDs from ATS6
            evidence_items: List of evidence item IDs from ATS5
            approved_niche_candidates: List of approved niche provider candidate IDs from ATS7
            correlation_id: Request correlation ID

        Returns:
            LonglistProposalResponse with ranked suppliers

        Raises:
            ValueError: If need not found or validation fails
        """
        # Validate need exists
        need = self.need_repo.get_by_id(need_id)
        if not need:
            raise ValueError(f"Need {need_id} not found")

        # Retrieve panel matches
        # If empty list provided, use ALL panel matches for this need
        if matched_panels:
            panel_matches = self.db.query(PanelMatch).filter(
                PanelMatch.id.in_([UUID(pm_id) for pm_id in matched_panels])
            ).all()
        else:
            panel_matches = self.db.query(PanelMatch).filter(
                PanelMatch.need_id == need_id
            ).all()

        # Retrieve evidence items
        # If empty list provided, use ALL evidence for this need
        if evidence_items:
            evidence_list = self.db.query(SupplierEvidenceItem).filter(
                SupplierEvidenceItem.id.in_([UUID(ev_id) for ev_id in evidence_items])
            ).all()
        else:
            evidence_list = self.db.query(SupplierEvidenceItem).filter(
                SupplierEvidenceItem.need_id == need_id
            ).all()

        # Retrieve approved niche candidates
        niche_candidates = self.db.query(ProviderCandidate).filter(
            ProviderCandidate.id.in_([UUID(nc_id) for nc_id in approved_niche_candidates]),
            ProviderCandidate.review_status == "approved"
        ).all() if approved_niche_candidates else []

        # Build supplier ranking map
        supplier_scores = self._rank_suppliers(panel_matches, evidence_list, niche_candidates)

        # Enforce citation requirement
        uncited_suppliers = [
            supplier_id for supplier_id, data in supplier_scores.items()
            if not data["citations"]
        ]
        if uncited_suppliers:
            raise ValueError(
                f"Uncited suppliers rejected: {', '.join(uncited_suppliers)}. "
                "Every ranked supplier must carry evidence_citations or approved research citations."
            )

        # Create ranked suppliers list
        ranked_supplier_records = []
        for rank, (supplier_id, data) in enumerate(sorted(
            supplier_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        ), start=1):
            ranked_supplier_records.append({
                "supplier_id": supplier_id,
                "rank": rank,
                "panel_source": data["panel_source"],
                "evidence_citations": data["citations"],
                "rank_rationale": data["rationale"],
                "confidence": data["confidence"],
            })

        # Check evidence limited flag
        evidence_limited_flag = need.evidence_limited_flag or len(evidence_list) == 0

        # Create proposal record
        proposal = LonglistProposal(
            id=uuid.uuid4(),
            need_id=need_id,
            ranked_suppliers=json.dumps([]),  # Will be populated via ranked supplier records
            evidence_limited_flag=evidence_limited_flag,
            review_status="pending",
        )
        proposal = self.proposal_repo.create(proposal)

        # Create ranked supplier records
        ranked_supplier_objects = []
        for ranked_data in ranked_supplier_records:
            ranked_supplier = LonglistRankedSupplier(
                id=uuid.uuid4(),
                proposal_id=proposal.id,
                supplier_id=ranked_data["supplier_id"],
                rank=ranked_data["rank"],
                panel_source=ranked_data["panel_source"],
                evidence_citations=json.dumps(ranked_data["evidence_citations"]),
                rank_rationale=ranked_data["rank_rationale"],
                confidence=ranked_data["confidence"],
            )
            self.db.add(ranked_supplier)
            ranked_supplier_objects.append(ranked_supplier)

        self.db.commit()
        for rs in ranked_supplier_objects:
            self.db.refresh(rs)

        # Write audit event
        audit_event = AuditEvent(
            need_id=need_id,
            correlation_id=correlation_id,
            step_code="ATS8",
            agent_code="AGN2",
            tool_code=None,
            actor_type="system",
            actor_id="longlist_proposal_service",
            outcome="proposal_generated",
            severity="info",
            payload_ref=f"Generated proposal {proposal.id} with {len(ranked_supplier_records)} ranked suppliers",
        )
        self.audit_repo.create(audit_event)

        # Build response
        ranked_suppliers_response = [
            RankedSupplierResponse(
                ranked_supplier_id=rs.id,
                supplier_id=rs.supplier_id,
                rank=rs.rank,
                panel_source=rs.panel_source,
                evidence_citations=[
                    EvidenceCitation(
                        source_reference=cit.get("source_reference", ""),
                        citation_text=cit.get("citation_text", "")
                    )
                    for cit in json.loads(rs.evidence_citations)
                ],
                rank_rationale=rs.rank_rationale,
                confidence=rs.confidence,
            )
            for rs in ranked_supplier_objects
        ]

        return LonglistProposalResponse(
            proposal_id=proposal.id,
            need_id=need_id,
            ranked_suppliers=ranked_suppliers_response,
            evidence_limited_flag=evidence_limited_flag,
            proposal_status=proposal.review_status,
            reviewed_by=None,
            reviewed_at=None,
            correlation_id=correlation_id,
        )

    def _rank_suppliers(
        self,
        panel_matches: List[PanelMatch],
        evidence_items: List[SupplierEvidenceItem],
        niche_candidates: List[ProviderCandidate],
    ) -> dict:
        """Rank suppliers based on panel matches, evidence, and niche research.

        Returns:
            Dictionary mapping supplier_id to ranking data with citations
        """
        supplier_scores: dict = {}

        # Process panel matches
        for pm in panel_matches:
            if pm.supplier_id not in supplier_scores:
                supplier_scores[pm.supplier_id] = {
                    "score": 0.0,
                    "panel_source": pm.panel_source,
                    "citations": [],
                    "rationale": "",
                    "confidence": 0.8,
                }
            supplier_scores[pm.supplier_id]["score"] += 50.0
            # Panel membership itself is evidence - add panel source as citation
            supplier_scores[pm.supplier_id]["citations"].append({
                "source_reference": pm.panel_source,
                "citation_text": f"Pre-qualified supplier on panel: {pm.panel_source} (functional group: {pm.functional_group or 'N/A'})",
            })
            supplier_scores[pm.supplier_id]["rationale"] += f"Panel match: {pm.panel_source}; "

        # Process evidence items
        for ev in evidence_items:
            if ev.supplier_id not in supplier_scores:
                supplier_scores[ev.supplier_id] = {
                    "score": 0.0,
                    "panel_source": "evidence-based",
                    "citations": [],
                    "rationale": "",
                    "confidence": 0.7,
                }
            supplier_scores[ev.supplier_id]["score"] += 30.0 * (ev.quality_rating or 1.0)
            supplier_scores[ev.supplier_id]["citations"].append({
                "source_reference": ev.source_reference,
                "citation_text": ev.citation_text,
            })
            supplier_scores[ev.supplier_id]["rationale"] += f"Evidence: {ev.evidence_type} ({ev.source_system}); "

        # Process niche candidates
        for nc in niche_candidates:
            if nc.supplier_id and nc.supplier_id not in supplier_scores:
                supplier_scores[nc.supplier_id] = {
                    "score": 0.0,
                    "panel_source": "niche-research",
                    "citations": [],
                    "rationale": "",
                    "confidence": 0.6,
                }
            if nc.supplier_id:
                supplier_scores[nc.supplier_id]["score"] += 40.0
                # Parse source_citations JSON
                try:
                    niche_citations = json.loads(nc.source_citations) if nc.source_citations else []
                    for cit in niche_citations:
                        supplier_scores[nc.supplier_id]["citations"].append({
                            "source_reference": cit.get("source", "niche-research"),
                            "citation_text": cit.get("citation", nc.capability_gap),
                        })
                except (json.JSONDecodeError, TypeError):
                    supplier_scores[nc.supplier_id]["citations"].append({
                        "source_reference": "niche-research",
                        "citation_text": nc.capability_gap,
                    })
                supplier_scores[nc.supplier_id]["rationale"] += f"Niche research: {nc.candidate_name}; "

        return supplier_scores
