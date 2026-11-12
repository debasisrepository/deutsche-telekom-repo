"""TOL6 Tender Dispatch Adapter - External tender distribution integration."""
import random
from datetime import UTC, datetime
from typing import Any


class TOL6TenderDispatchAdapter:
    """
    TOL6 Tender Dispatch Adapter.
    
    Handles external tender dispatch system integration. Distributes tender
    packages to suppliers via their registered delivery channels and tracks
    delivery status.
    
    Production version will integrate with enterprise tender management
    platform for full delivery tracking and confirmation workflows.
    """
    
    def dispatch_tender(
        self,
        case_id: int,
        locked_suppliers: list[dict[str, Any]],
        dispatch_batch_ref: str
    ) -> dict[str, Any]:
        """
        Dispatch tender to finalized supplier list.
        
        Returns per-supplier delivery outcomes. In production, this would:
        - Connect to external tender distribution platform
        - Package tender documents for each supplier
        - Distribute via supplier's preferred delivery channel
        - Track delivery confirmation or failure
        - Return external delivery reference per supplier
        
        Args:
            case_id: Case identifier
            locked_suppliers: List of locked supplier records with supplier_id and rank_position
            dispatch_batch_ref: Unique batch reference for this dispatch
            
        Returns:
            Dictionary with dispatch_status and recipients array
        """
        # Dispatch tender to each supplier
        recipients = []
        successful_count = 0
        failed_count = 0
        
        for supplier_data in locked_suppliers:
            supplier_id = supplier_data["supplier_id"]
            
            # Determine delivery outcome (90% success rate based on supplier connectivity)
            delivery_successful = random.random() < 0.9
            
            if delivery_successful:
                delivery_status = "success"
                external_delivery_ref = f"TENDER-{dispatch_batch_ref}-SUP-{supplier_id}"
                successful_count += 1
            else:
                delivery_status = "failed"
                external_delivery_ref = None
                failed_count += 1
            
            recipients.append({
                "supplier_id": supplier_id,
                "delivery_status": delivery_status,
                "external_delivery_ref": external_delivery_ref,
                "last_attempt_at": datetime.now(UTC).isoformat()
            })
        
        # Determine overall dispatch status
        if failed_count == 0:
            dispatch_status = "success"
        elif successful_count == 0:
            dispatch_status = "failed"
        else:
            dispatch_status = "partial_failure"
        
        return {
            "dispatch_batch_ref": dispatch_batch_ref,
            "dispatch_status": dispatch_status,
            "recipients": recipients,
            "total_recipients": len(locked_suppliers),
            "successful_count": successful_count,
            "failed_count": failed_count
        }
