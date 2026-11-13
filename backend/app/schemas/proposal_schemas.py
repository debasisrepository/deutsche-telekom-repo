"""Schemas for longlist proposal generation (ATS8)."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvidenceCitation(BaseModel):
    """Single evidence citation for a ranked supplier."""
    source_reference: str
    citation_text: str


class RankedSupplierResponse(BaseModel):
    """Response schema for a ranked supplier in the proposal."""
    ranked_supplier_id: UUID
    supplier_id: str
    rank: int
    panel_source: str
    evidence_citations: List[EvidenceCitation]
    rank_rationale: str
    confidence: float

    model_config = ConfigDict(from_attributes=True)


class LonglistProposalRequest(BaseModel):
    """Request schema for longlist proposal generation (ATS8)."""
    need_id: str = Field(..., description="Need ID for the proposal")
    matched_panels: List[str] = Field(..., description="Panel match IDs from ATS6")
    evidence_items: List[str] = Field(..., description="Evidence item IDs from ATS5")
    approved_niche_candidates: Optional[List[str]] = Field(None, description="Approved niche provider candidate IDs from ATS7")
    supplier_count_rules: Optional[dict] = Field(None, description="Supplier count rules for validation")


class LonglistProposalResponse(BaseModel):
    """Response schema for longlist proposal generation (ATS8)."""
    proposal_id: UUID
    need_id: UUID
    ranked_suppliers: List[RankedSupplierResponse]
    evidence_limited_flag: bool
    proposal_status: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    correlation_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
