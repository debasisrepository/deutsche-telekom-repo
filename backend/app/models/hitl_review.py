from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HITLReview(Base):
    """
    Human-in-the-loop review record for AMBER steps (extraction, classification).
    Preserves generated-versus-final distinction for audit compliance.
    """
    __tablename__ = "hitl_review"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, index=True)
    review_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # extraction, classification
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # pending, approved, rejected
    assigned_role: Mapped[str | None] = mapped_column(String(50), nullable=True)  # role authorized to review
    decision: Mapped[str | None] = mapped_column(String(50), nullable=True)  # approve, edit, reject, override
    reviewer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    generated_payload: Mapped[str | None] = mapped_column(Text, nullable=True)  # AI-generated output as JSONB text
    final_payload: Mapped[str | None] = mapped_column(Text, nullable=True)  # Human-confirmed output as JSONB text
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True
    )
