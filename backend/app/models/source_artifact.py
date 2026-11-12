from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.need_case import NeedCase


class SourceArtifact(Base):
    __tablename__ = "source_artifact"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    source_channel: Mapped[str] = mapped_column(String(50), nullable=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC),
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
    
    # Relationships
    case: Mapped[NeedCase] = relationship("NeedCase", back_populates="source_artifacts")
