"""Case Evidence Model - Evidence items linked to case with supplier citations."""
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CaseEvidence(Base):
    """Evidence record linking case to historical supplier data.
    
    Captures evidence retrieved from TOL2 supplier knowledge base,
    normalized and stored per case with evidence_found flag.
    """
    __tablename__ = "case_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, index=True)
    supplier_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("supplier.id"), nullable=True, index=True)
    historical_order_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("historical_order.id"), nullable=True)
    commissioned_sow_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("commissioned_sow.id"), nullable=True)
    citation_label: Mapped[str] = mapped_column(Text, nullable=False)
    citation_ref: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_found: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
