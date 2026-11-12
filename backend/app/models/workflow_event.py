from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WorkflowEvent(Base):
    __tablename__ = "workflow_event"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    from_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_state: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSONB stored as TEXT
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC),
        index=True
    )
