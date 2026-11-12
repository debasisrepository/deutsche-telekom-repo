"""Supplier Model - Supplier master data with evidence retrieval status."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Supplier(Base):
    """Supplier master record with evidence source status.
    
    Tracks suppliers from panel registries and historical evidence sources.
    Used as foreign key target for evidence citations and longlist proposals.
    """
    __tablename__ = "supplier"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    contact_endpoint: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_source_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
