"""Longlist-related Pydantic schemas."""

from pydantic import BaseModel, ConfigDict


class SupplierResponse(BaseModel):
    """Supplier information in evidence response."""
    id: int
    supplier_code: str
    display_name: str
    status: str
    
    model_config = ConfigDict(from_attributes=True)


class EvidenceItemResponse(BaseModel):
    """Evidence item with supplier and citation details."""
    id: int
    case_id: int
    supplier: SupplierResponse | None
    citation_label: str
    citation_ref: str
    evidence_summary: str
    evidence_found: bool
    created_at: str | None
    
    model_config = ConfigDict(from_attributes=True)


class CaseEvidenceResponse(BaseModel):
    """Case evidence list response."""
    case_id: int
    case_number: str
    evidence_items: list[EvidenceItemResponse]
    total: int
