"""Validation Repository - Data access for policy validations."""
from sqlalchemy.orm import Session

from app.models.policy_validation import PolicyValidation


class ValidationRepository:
    """Repository for policy validation data access."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, validation_id: int) -> PolicyValidation | None:
        """
        Get validation by ID.
        
        Args:
            validation_id: Validation identifier
            
        Returns:
            PolicyValidation or None if not found
        """
        return self.session.query(PolicyValidation).filter(
            PolicyValidation.id == validation_id
        ).first()
    
    def get_latest_by_case(self, case_id: int, validation_type: str) -> PolicyValidation | None:
        """
        Get latest validation for a case by type.
        
        Args:
            case_id: Case identifier
            validation_type: Type of validation (e.g., 'supplier_count')
            
        Returns:
            Latest PolicyValidation or None if not found
        """
        return self.session.query(PolicyValidation).filter(
            PolicyValidation.case_id == case_id,
            PolicyValidation.validation_type == validation_type
        ).order_by(PolicyValidation.validated_at.desc()).first()
    
    def list_by_case(self, case_id: int) -> list[PolicyValidation]:
        """
        List all validations for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of PolicyValidation records ordered by validated_at
        """
        return self.session.query(PolicyValidation).filter(
            PolicyValidation.case_id == case_id
        ).order_by(PolicyValidation.validated_at.desc()).all()
    
    def create(self, validation: PolicyValidation) -> PolicyValidation:
        """
        Create new validation record.
        
        Args:
            validation: PolicyValidation model to persist
            
        Returns:
            Persisted PolicyValidation with ID
        """
        self.session.add(validation)
        self.session.flush()
        return validation
