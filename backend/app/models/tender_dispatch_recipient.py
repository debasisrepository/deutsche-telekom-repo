"""Tender Dispatch Recipient Model - Per-supplier delivery outcome."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TenderDispatchRecipient(Base):
    """Per-supplier tender dispatch outcome.
    
    Records delivery status, external delivery reference, and last attempt
    timestamp for each supplier in the dispatch batch.
    """
    __tablename__ = "tender_dispatch_recipient"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dispatch_id: Mapped[int] = mapped_column(Integer, ForeignKey("tender_dispatch.id"), nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("supplier.id"), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # success, failed
    external_delivery_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    last_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
