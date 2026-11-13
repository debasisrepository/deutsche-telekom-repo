from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PanelMappingRequest(BaseModel):
    """ATS6 panel mapping request."""

    need_id: UUID
    need_category: str = Field(..., description="Category of the need for panel mapping")


class CandidateSupplier(BaseModel):
    """A single candidate supplier from panel/functional-group mapping."""

    panel_match_id: UUID
    supplier_id: str
    panel_source: str
    functional_group: str
    provenance_ref: str

    model_config = ConfigDict(from_attributes=True)


class PanelMappingResponse(BaseModel):
    """ATS6 panel mapping response."""

    need_id: UUID
    candidate_suppliers: list[CandidateSupplier]
    coverage_gap_flag: bool = Field(
        ...,
        description="True when registry lacks adequate coverage, triggering ATS7",
    )
    correlation_id: str

    model_config = ConfigDict(from_attributes=True)
