import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VmsHandoff(Base):
    __tablename__ = "vms_handoffs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    need_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("needs.id"), nullable=False, index=True)
    handover_confirmation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    vms_reference_id: Mapped[str] = mapped_column(String(200), nullable=True)
    workflow_status: Mapped[str] = mapped_column(String(100), nullable=False, default="vms_routed_terminal")
    request_payload_json: Mapped[str] = mapped_column(Text, nullable=True)
    response_payload_json: Mapped[str] = mapped_column(Text, nullable=True)
    error_detail: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
