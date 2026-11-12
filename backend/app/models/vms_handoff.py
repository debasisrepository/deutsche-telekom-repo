"""VMS Handoff Model - Records single-resource case VMS routing"""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VMSHandoff(Base):
    """
    Records Vendor Management System handoff for single-resource cases.
    Tracks VMS reference ID, handoff status, and request snapshot.
    """
    __tablename__ = "vms_handoff"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, unique=True)
    vms_reference_id: Mapped[str] = mapped_column(String(100), nullable=False)
    handoff_status: Mapped[str] = mapped_column(String(50), nullable=False)  # success, failed, pending
    request_snapshot: Mapped[str] = mapped_column(Text, nullable=False)  # JSONB stored as text
    handed_off_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    requirement_tags: Mapped[str] = mapped_column(String(500), nullable=True)
