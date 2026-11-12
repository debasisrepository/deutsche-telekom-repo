"""Case Mapping Model - Links cases to panels and functional groups."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CaseMapping(Base):
    """Case mapping to panel and functional group.
    
    Records the mapping of a case to enterprise panel and functional group.
    Stores mapping status and rationale inputs for audit trail.
    """
    __tablename__ = "case_mapping"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, index=True)
    panel_id: Mapped[int] = mapped_column(Integer, ForeignKey("panel.id"), nullable=False, index=True)
    functional_group_id: Mapped[int] = mapped_column(Integer, ForeignKey("functional_group.id"), nullable=False, index=True)
    mapping_status: Mapped[str] = mapped_column(String(50), nullable=False, default="proposed")
    rationale_inputs: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
