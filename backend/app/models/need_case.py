from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.normalized_need import NormalizedNeed
    from app.models.source_artifact import SourceArtifact
    from app.models.vms_handoff import VMSHandoff


class NeedCase(Base):
    __tablename__ = "need_case"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    inbound_channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    workflow_state: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    next_action: Mapped[str] = mapped_column(String(100), nullable=False)
    final_classification: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC),
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )
    
    # Relationships
    normalized_need: Mapped[NormalizedNeed] = relationship("NormalizedNeed", back_populates="case", uselist=False)
    source_artifacts: Mapped[list[SourceArtifact]] = relationship("SourceArtifact", back_populates="case")
    vms_handoff: Mapped[VMSHandoff | None] = relationship("VMSHandoff", uselist=False)
