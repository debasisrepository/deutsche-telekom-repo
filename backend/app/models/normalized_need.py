from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.need_case import NeedCase


class NormalizedNeed(Base):
    __tablename__ = "normalized_need"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, unique=True, index=True)
    mandatory_fields: Mapped[str] = mapped_column(Text, nullable=False)  # JSONB stored as TEXT in SQLite
    sourced_fields: Mapped[str] = mapped_column(Text, nullable=False)
    derived_fields: Mapped[str] = mapped_column(Text, nullable=False)
    completeness_score: Mapped[float] = mapped_column(Float, nullable=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )
    
    # Relationships
    case: Mapped[NeedCase] = relationship("NeedCase", back_populates="normalized_need")
