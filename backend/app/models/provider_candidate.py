import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProviderCandidate(Base):
    __tablename__ = "provider_candidates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    need_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("needs.id"), nullable=False, index=True)
    candidate_name: Mapped[str] = mapped_column(String(200), nullable=False)
    supplier_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    capability_gap: Mapped[str] = mapped_column(Text, nullable=False)
    source_citations: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array as text
    review_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    reviewer_notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
