import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TenderDispatch(Base):
    __tablename__ = "tender_dispatches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    longlist_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("longlists.id"), nullable=False, index=True)
    dispatch_batch_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    supplier_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    supplier_contact: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    dispatch_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delivery_confirmation_ref: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
