"""Proposal Supplier Model - Ranked supplier in a longlist proposal."""
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.longlist_proposal import LonglistProposal
    from app.models.supplier import Supplier


class ProposalSupplier(Base):
    """Ranked supplier in a longlist proposal.
    
    Links supplier to proposal with ranking position, score, and citation status.
    Used for generating ranked supplier longlists with evidence grounding.
    """
    __tablename__ = "proposal_supplier"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    proposal_id: Mapped[int] = mapped_column(Integer, ForeignKey("longlist_proposal.id"), nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("supplier.id"), nullable=False, index=True)
    rank_position: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation_status: Mapped[str] = mapped_column(String(50), nullable=False, default="recommended")
    ranking_score: Mapped[float] = mapped_column(Float, nullable=False)
    citation_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
    
    # Relationships
    proposal: Mapped["LonglistProposal"] = relationship("LonglistProposal", back_populates="proposal_suppliers")
    supplier: Mapped["Supplier"] = relationship("Supplier")
