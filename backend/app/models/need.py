import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Need(Base):
    __tablename__ = "needs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_unit_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    channel_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    arrival_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    raw_artifact_ref: Mapped[str] = mapped_column(Text, nullable=True)
    normalized_payload_json: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="normalized", index=True)
    classification_verdict: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    classification_confidence: Mapped[float] = mapped_column(nullable=True)
    evidence_limited_flag: Mapped[bool] = mapped_column(nullable=False, default=False, server_default="0")
    correlation_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
