"""Historical Order Model - Records past completed orders for evidence retrieval."""
from datetime import UTC, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HistoricalOrder(Base):
    """Historical order record used as evidence source.
    
    Links completed orders to suppliers for citation in longlist proposals.
    """
    __tablename__ = "historical_order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_order_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    service_domain: Mapped[str] = mapped_column(String(100), nullable=False)
    completion_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC)
    )
