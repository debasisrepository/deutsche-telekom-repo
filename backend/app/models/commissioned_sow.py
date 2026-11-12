"""Commissioned SoW Model - Records past statements of work for evidence retrieval."""
from datetime import UTC, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CommissionedSoW(Base):
    """Commissioned Statement of Work record used as evidence source.
    
    Links past SoWs to suppliers for citation in longlist proposals.
    """
    __tablename__ = "commissioned_sow"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_sow_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    scope_summary: Mapped[str] = mapped_column(Text, nullable=False)
    signed_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
