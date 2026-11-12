"""TOL4 Longlist Validation Adapter - Deterministic supplier-count rule validator."""
import json
from typing import Any


class TOL4LonglistValidationAdapter:
    """
    TOL4 adapter enforcing deterministic supplier-count validation rules.
    
    Implements the 3-6 supplier count rule as specified in FR-021.
    This is a deterministic rule engine with no AI behavior.
    """
    
    def validate_supplier_count(self, supplier_count: int) -> dict[str, Any]:
        """
        Validate supplier count against the 3-6 rule.
        
        Args:
            supplier_count: Number of suppliers in the longlist
            
        Returns:
            Validation result dictionary with:
                - validation_result: 'valid', 'invalid_low', or 'invalid_high'
                - supplier_count: Input count
                - rule_snapshot: JSONB snapshot of rules applied
                - validation_message: Human-readable explanation
        """
        # Apply deterministic 3-6 supplier count rule
        if supplier_count < 3:
            validation_result = "invalid_low"
            validation_message = f"Longlist has {supplier_count} supplier(s), below minimum of 3"
        elif 3 <= supplier_count <= 6:
            validation_result = "valid"
            validation_message = f"Longlist has {supplier_count} supplier(s), within valid range of 3-6"
        else:
            validation_result = "invalid_high"
            validation_message = f"Longlist has {supplier_count} supplier(s), above maximum of 6"
        
        # Create rule snapshot for audit compliance
        rule_snapshot = {
            "rule_type": "supplier_count_band",
            "min_suppliers": 3,
            "max_suppliers": 6,
            "applied_count": supplier_count,
            "rule_version": "1.0"
        }
        
        return {
            "validation_result": validation_result,
            "supplier_count": supplier_count,
            "rule_snapshot": json.dumps(rule_snapshot),
            "validation_message": validation_message
        }
