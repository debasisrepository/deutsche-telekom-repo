"""Longlist Policy Service - Validation and enforcement for longlist policies."""
from typing import Any

from sqlalchemy.orm import Session

from app.models.policy_validation import PolicyValidation
from app.repositories.lock_repository import LockRepository
from app.repositories.longlist_repository import LonglistRepository
from app.repositories.validation_repository import ValidationRepository
from app.services.rules.agn5_rule_engine import AGN5RuleEngine


class LonglistPolicyService:
    """
    Service for validating longlist policies.
    
    Implements citation coverage validation and supplier-count validation
    before longlist finalization and locking.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.longlist_repo = LonglistRepository(session)
        self.lock_repo = LockRepository(session)
        self.validation_repo = ValidationRepository(session)
        self.agn5_engine = AGN5RuleEngine(session)
    
    def validate_citation_coverage(self, case_id: int) -> dict[str, Any]:
        """
        Validate that all recommended suppliers have evidence citations.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Validation result dictionary with citation_complete flag
        """
        # Get latest proposal
        proposals = self.longlist_repo.list_case_proposals(case_id)
        if not proposals:
            proposal = None
        else:
            proposal = proposals[0]  # Get latest (already ordered by version_no desc)
        if not proposal:
            return {
                "case_id": case_id,
                "citation_complete": False,
                "message": "No longlist proposal found"
            }
        
        # Get proposal suppliers
        proposal_suppliers = self.longlist_repo.get_proposal_suppliers(proposal.id)
        
        # Check citation completeness for each supplier
        incomplete_suppliers = []
        for ps in proposal_suppliers:
            if not ps.citation_complete:
                incomplete_suppliers.append({
                    "supplier_id": ps.supplier_id,
                    "supplier_code": ps.supplier.supplier_code if ps.supplier else "unknown",
                    "rank_position": ps.rank_position
                })
        
        citation_complete = len(incomplete_suppliers) == 0
        
        return {
            "case_id": case_id,
            "proposal_id": proposal.id,
            "total_suppliers": len(proposal_suppliers),
            "citation_complete": citation_complete,
            "incomplete_suppliers": incomplete_suppliers,
            "message": "All suppliers have citations" if citation_complete else f"{len(incomplete_suppliers)} supplier(s) missing citations"
        }
    
    def validate_supplier_count(self, case_id: int) -> dict[str, Any]:
        """
        Validate supplier count against the 3-6 rule via AGN5/TOL4.
        
        Creates and persists a policy_validation record with the result.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Validation result dictionary with validation_result and validation_id
        """
        # Get latest proposal
        proposals = self.longlist_repo.list_case_proposals(case_id)
        if not proposals:
            raise ValueError(f"No longlist proposal found for case {case_id}")
        proposal = proposals[0]  # Get latest (already ordered by version_no desc)
        
        # Get proposal suppliers to count
        proposal_suppliers = self.longlist_repo.get_proposal_suppliers(proposal.id)
        supplier_count = len(proposal_suppliers)
        
        # Invoke AGN5 with TOL4 adapter
        validation_result_data = self.agn5_engine.validate_supplier_count_with_tol4(supplier_count)
        
        # Create policy_validation record
        policy_validation = PolicyValidation(
            case_id=case_id,
            validation_type="supplier_count",
            supplier_count=supplier_count,
            validation_result=validation_result_data["validation_result"],
            rule_snapshot=validation_result_data["rule_snapshot"],
            requirement_tags="REQ-DOMAIN-009"
        )
        
        self.session.add(policy_validation)
        self.session.flush()
        
        return {
            "validation_id": policy_validation.id,
            "case_id": case_id,
            "validation_type": "supplier_count",
            "supplier_count": supplier_count,
            "validation_result": validation_result_data["validation_result"],
            "rule_snapshot": validation_result_data["rule_snapshot"],
            "validation_message": validation_result_data["validation_message"],
            "validated_at": policy_validation.validated_at.isoformat()
        }
    
    def assert_lock_preconditions(self, case_id: int) -> None:
        """
        Assert lock preconditions before allowing lock action.
        
        Lock precondition: latest supplier-count validation must be 'valid'.
        
        Args:
            case_id: Case identifier
            
        Raises:
            ValueError: If preconditions not met
        """
        # Get latest validation for this case
        latest_validation = self.validation_repo.get_latest_by_case(
            case_id=case_id,
            validation_type="supplier_count"
        )
        
        if not latest_validation:
            raise ValueError(
                "Supplier count must be validated before locking. "
                "Run POST /api/v1/cases/{caseId}/validations/supplier-count first."
            )
        
        if latest_validation.validation_result != "valid":
            raise ValueError(
                f"Supplier count validation result is '{latest_validation.validation_result}'. "
                f"Lock requires 'valid' result (3-6 suppliers)."
            )
    
    def assert_dispatch_preconditions(self, case_id: int) -> None:
        """
        Assert dispatch preconditions before allowing dispatch action.
        
        Dispatch precondition: locked longlist must exist.
        
        Args:
            case_id: Case identifier
            
        Raises:
            ValueError: If preconditions not met
        """
        # Check if case has locked longlist
        locked_longlist = self.lock_repo.get_locked_longlist_by_case(case_id)
        
        if not locked_longlist:
            raise ValueError(
                "Case must be locked before dispatch. "
                "Run POST /api/v1/cases/{caseId}/lock first."
            )
        
        if locked_longlist.lock_status != "locked":
            raise ValueError(
                f"Longlist lock status is '{locked_longlist.lock_status}'. "
                f"Dispatch requires 'locked' status."
            )
