"""Tender Dispatch Model - Tender distribution event with batch reference."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TenderDispatch(Base):
    """Tender dispatch record for batch tender distribution (ATS12).
    
    Records the overall dispatch event with batch reference, status,
    and actor information. Per-supplier outcomes stored in tender_dispatch_recipient.
    """
    __tablename__ = "tender_dispatch"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    locked_longlist_id: Mapped[int] = mapped_column(Integer, ForeignKey("locked_longlist.id"), nullable=False, unique=True)
    dispatch_batch_ref: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    dispatch_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # success, partial_failure, failed
    dispatched_by: Mapped[str] = mapped_column(String(50), nullable=False)
    dispatched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
