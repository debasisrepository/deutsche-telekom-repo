import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SupplierEvidenceItem(Base):
    __tablename__ = "supplier_evidence_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    need_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("needs.id"), nullable=False, index=True)
    supplier_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_system: Mapped[str] = mapped_column(String(64), nullable=False, server_default="SEED")
    source_reference: Mapped[str] = mapped_column(Text, nullable=False)
    service_category: Mapped[str] = mapped_column(String(128), nullable=False, server_default="general")
    business_unit_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    delivery_period: Mapped[str | None] = mapped_column(String(128), nullable=True)
    quality_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    citation_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    evidence_snapshot_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence_limited_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
