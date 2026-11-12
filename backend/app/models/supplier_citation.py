"""Supplier Citation Model - Links proposal suppliers to case evidence.

Note: This model is prepared for future longlist implementation.
The foreign key to proposal_supplier will be added when that table is created.
For now, proposal_supplier_id is stored as an integer without FK constraint.
"""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SupplierCitation(Base):
    """Citation link from longlist proposal supplier to evidence.
    
    Enforces evidence-grounding rule: every recommended supplier must have
    at least one citation pointing to case evidence.
    
    Note: proposal_supplier_id FK will be added in future migration when
    proposal_supplier table is created.
    """
    __tablename__ = "supplier_citation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    proposal_supplier_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False, 
        index=True
    )
    case_evidence_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("case_evidence.id", name="fk_supplier_citation_case_evidence"),
        nullable=False, 
        index=True
    )
    citation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    citation_ref: Mapped[str] = mapped_column(Text, nullable=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
