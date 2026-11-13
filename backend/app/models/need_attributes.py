import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NeedAttributes(Base):
    __tablename__ = "need_attributes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    need_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("needs.id"), nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(String(200), nullable=True)
    scope_description: Mapped[str] = mapped_column(Text, nullable=True)
    estimated_volume_duration: Mapped[str] = mapped_column(String(500), nullable=True)
    required_skills: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array as text
    budget_indication: Mapped[str] = mapped_column(String(200), nullable=True)
    delivery_location: Mapped[str] = mapped_column(String(500), nullable=True)
    field_confidence: Mapped[str] = mapped_column(Text, nullable=True)  # JSON object as text
    schema_valid: Mapped[bool] = mapped_column(nullable=False, default=True, server_default="1")
    review_status: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    reviewed_by: Mapped[str] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
