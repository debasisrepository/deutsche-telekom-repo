"""Classification Result Model - Stores classification verdicts with override tracking"""
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ClassificationResult(Base):
    """
    Classification verdict record tracking AI and confirmed classifications.
    Supports override tracking per REQ-DOMAIN-005.
    """
    __tablename__ = "classification_result"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, unique=True, index=True)
    ai_verdict: Mapped[str] = mapped_column(String(50), nullable=False)  # single_resource or it_service
    confirmed_verdict: Mapped[str] = mapped_column(String(50), nullable=False)  # Final confirmed verdict
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    rationale_inputs: Mapped[str] = mapped_column(Text, nullable=False)  # JSONB as text
    overridden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        index=True
    )
