"""Locked Longlist Model - Immutable snapshot of finalized supplier set."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LockedLonglist(Base):
    """Locked longlist record created before tender dispatch (ATS11).
    
    Represents an immutable snapshot of the finalized supplier set.
    Once locked, the supplier list cannot be altered without explicit unlock.
    Lock event is audited with actor and timestamp.
    """
    __tablename__ = "locked_longlist"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, unique=True, index=True)
    source_proposal_id: Mapped[int] = mapped_column(Integer, ForeignKey("longlist_proposal.id"), nullable=False)
    lock_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # locked, unlocked
    locked_by: Mapped[str] = mapped_column(String(50), nullable=False)
    locked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
