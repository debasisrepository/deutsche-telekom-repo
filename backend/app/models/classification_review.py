import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ClassificationReview(Base):
    __tablename__ = "classification_reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    need_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("needs.id"), nullable=False, index=True)
    classification_verdict: Mapped[str] = mapped_column(String(50), nullable=False)
    classification_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    rationale: Mapped[str] = mapped_column(Text, nullable=True)
    review_decision: Mapped[str] = mapped_column(String(50), nullable=True)
    reviewer_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    escalation_required: Mapped[bool] = mapped_column(default=False, nullable=False)
    exemplars_referenced: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array as text
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
