"""Panel Model - Enterprise panel master data for supplier mapping."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Panel(Base):
    """Enterprise panel master record.
    
    Tracks approved supplier panels from enterprise registry.
    Used for mapping cases to eligible supplier pools.
    """
    __tablename__ = "panel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    panel_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    panel_name: Mapped[str] = mapped_column(String(255), nullable=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
