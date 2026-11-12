"""Locked Supplier Model - Individual supplier in locked longlist snapshot."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LockedSupplier(Base):
    """Individual supplier record in locked longlist.
    
    Immutable snapshot of supplier at time of lock. This is the definitive
    set used for tender dispatch (ATS12).
    """
    __tablename__ = "locked_supplier"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    locked_longlist_id: Mapped[int] = mapped_column(Integer, ForeignKey("locked_longlist.id"), nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("supplier.id"), nullable=False, index=True)
    final_rank_position: Mapped[int] = mapped_column(Integer, nullable=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
