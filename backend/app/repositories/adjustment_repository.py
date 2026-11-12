"""Adjustment Repository - Data access for supplier adjustments."""
from sqlalchemy.orm import Session

from app.models.supplier_adjustment import SupplierAdjustment


class AdjustmentRepository:
    """Repository for supplier adjustment data access."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, adjustment_id: int) -> SupplierAdjustment | None:
        """
        Get adjustment by ID.
        
        Args:
            adjustment_id: Adjustment identifier
            
        Returns:
            SupplierAdjustment or None if not found
        """
        return self.session.query(SupplierAdjustment).filter(
            SupplierAdjustment.id == adjustment_id
        ).first()
    
    def list_by_case(self, case_id: int) -> list[SupplierAdjustment]:
        """
        List all adjustments for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of SupplierAdjustment records ordered by created_at
        """
        return self.session.query(SupplierAdjustment).filter(
            SupplierAdjustment.case_id == case_id
        ).order_by(SupplierAdjustment.created_at.desc()).all()
    
    def create(self, adjustment: SupplierAdjustment) -> SupplierAdjustment:
        """
        Create new adjustment record.
        
        Args:
            adjustment: SupplierAdjustment model to persist
            
        Returns:
            Persisted SupplierAdjustment with ID
        """
        self.session.add(adjustment)
        self.session.flush()
        return adjustment
