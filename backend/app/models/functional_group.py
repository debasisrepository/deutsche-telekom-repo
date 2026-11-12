"""Functional Group Model - Enterprise functional group master data for supplier mapping."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FunctionalGroup(Base):
    """Enterprise functional group master record.
    
    Tracks functional groups for supplier categorization.
    Used for mapping cases to relevant service categories.
    """
    __tablename__ = "functional_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    functional_group_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    functional_group_name: Mapped[str] = mapped_column(String(255), nullable=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
