from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EvidenceQueryRequest(BaseModel):
    """Request schema for evidence query (ATS5)."""
    need_id: str = Field(..., description="Need ID for evidence retrieval")
    service_type: Optional[str] = Field(None, description="Service type filter")
    required_skills: Optional[List[str]] = Field(None, description="Required skills filter")
    business_unit_id: Optional[str] = Field(None, description="Business unit filter")
    panel_filters: Optional[List[str]] = Field(None, description="Panel source filters")


class EvidenceItem(BaseModel):
    """Individual evidence item in response."""
    supplier_id: str
    evidence_type: str
    source_system: str
    source_reference: str
    service_category: str
    business_unit: Optional[str] = None
    delivery_period: Optional[str] = None
    quality_rating: Optional[float] = None
    citation_text: str
    is_seed_data: bool
    snapshot_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceQueryResponse(BaseModel):
    """Response schema for evidence query (ATS5)."""
    evidence_items: List[EvidenceItem]
    evidence_limited_flag: bool
    evidence_snapshot_timestamp: datetime
    correlation_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
