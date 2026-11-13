import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SupplierCountValidation(Base):
    __tablename__ = "supplier_count_validations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    proposal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("longlist_proposals.id"), nullable=False, index=True)
    supplier_count: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_verdict: Mapped[str] = mapped_column(String(50), nullable=False)
    violations: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array as text
    triggered_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
