from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NicheResearchRequest(BaseModel):
    """ATS7 niche provider research request."""

    need_id: UUID
    capability_gap: str = Field(..., description="Specific capability gap description")
    approved_source_list: list[str] = Field(..., description="Governed source list for research")
    existing_panel_matches: Optional[list[str]] = Field(
        default=None,
        description="Optional list of supplier_ids from existing panel matches",
    )


class NicheResearchDossierItem(BaseModel):
    """A single niche provider candidate from research."""

    provider_candidate_id: UUID
    candidate_name: str
    supplier_id: str
    capability_gap: str
    source_citations: list[str]  # JSON array of cited sources
    review_status: str
    review_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NicheResearchResponse(BaseModel):
    """ATS7 niche provider research response."""

    need_id: UUID
    niche_research_dossier: list[NicheResearchDossierItem]
    review_required: bool = Field(
        ...,
        description="True when reviewers must accept/modify/reject before ranking eligibility",
    )
    correlation_id: str

    model_config = ConfigDict(from_attributes=True)
