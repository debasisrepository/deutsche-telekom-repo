"""Policy Validation Model - Tracks supplier-count validation results."""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PolicyValidation(Base):
    """Policy validation record tracking rule enforcement outcomes.
    
    Stores validation results for supplier-count rules and other policy checks.
    Each validation captures the supplier count, validation result, rule snapshot,
    and validation timestamp for audit compliance.
    """
    __tablename__ = "policy_validation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("need_case.id"), nullable=False, index=True)
    validation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'supplier_count'
    supplier_count: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_result: Mapped[str] = mapped_column(String(50), nullable=False)  # 'valid', 'invalid_low', 'invalid_high'
    rule_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSONB snapshot of rules applied
    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(UTC),
        index=True
    )
    requirement_tags: Mapped[str | None] = mapped_column(Text, nullable=True)
