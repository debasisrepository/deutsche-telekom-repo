"""Supplier Adjustment Model - Captures add/remove supplier actions."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SupplierAdjustment(Base):
    """Supplier adjustment record tracking business-unit add/remove actions.
    
    Records every supplier addition or removal action on a longlist proposal,
    preserving actor, timestamp, change type, rationale, and resulting supplier count.
    Adjustment history remains visible before and after finalization.
    """
    __tablename__ = "supplier_adjustment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("supplier.id"), nullable=False, index=True)
    change_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'add' or 'remove'
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_id: Mapped[str] = mapped_column(String(50), nullable=False)  # User ID or system identifier
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC),
        index=True
    )
    resulting_supplier_count: Mapped[int] = mapped_column(Integer, nullable=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
