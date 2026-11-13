import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PanelMatch(Base):
    __tablename__ = "panel_matches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    need_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("needs.id"), nullable=False, index=True)
    supplier_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    panel_source: Mapped[str] = mapped_column(String(200), nullable=False)
    functional_group: Mapped[str] = mapped_column(String(200), nullable=True)
    provenance_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    coverage_gap_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
