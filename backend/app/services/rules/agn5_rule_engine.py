"""AGN5 Deterministic Rule Engine - ATS1, ATS4-ATS6, ATS9, ATS11-ATS12 guards"""
from typing import Any

from sqlalchemy.orm import Session

from app.adapters.tol2_supplier_kb_adapter import TOL2SupplierKBAdapter
from app.adapters.tol3_panel_mapping_adapter import TOL3PanelMappingAdapter
from app.adapters.tol4_longlist_validation_adapter import TOL4LonglistValidationAdapter
from app.adapters.tol5_vms_handover_adapter import TOL5VMSHandoverAdapter
from app.models.vms_handoff import VMSHandoff


class AGN5RuleEngine:
    """
    Deterministic rule engine for non-AI workflow steps.
    Handles: normalization, VMS routing, evidence retrieval coordination,
    mapping coordination, validation, lock/dispatch preconditions.
    """
    
    def __init__(self, session: Session | None = None):
        self.session = session
        self.tol2_adapter = TOL2SupplierKBAdapter()
        self.tol3_adapter = TOL3PanelMappingAdapter()
        self.tol4_adapter = TOL4LonglistValidationAdapter()
        self.tol5_adapter = TOL5VMSHandoverAdapter()
    
    def calculate_completeness_score(self, mandatory_fields: dict[str, Any]) -> float:
        """
        Calculate completeness score for normalized need (ATS1).
        
        Args:
            mandatory_fields: Dictionary of mandatory field values
            
        Returns:
            Completeness score between 0.0 and 1.0
        """
        if not mandatory_fields:
            return 0.0
        
        total_fields = len(mandatory_fields)
        filled_fields = sum(1 for v in mandatory_fields.values() if v)
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    def determine_initial_workflow_state(self, completeness_score: float) -> tuple[str, str]:
        """
        Determine initial workflow state and next action (ATS1).
        
        Returns:
            Tuple of (workflow_state, next_action)
        """
        if completeness_score >= 0.8:
            return ("intake_normalized", "Review extracted attributes")
        else:
            return ("intake_pending", "Complete missing mandatory fields")
    
    def validate_vms_routing_precondition(self, classification: str) -> bool:
        """
        Validate VMS handoff precondition (ATS4).
        
        Args:
            classification: Confirmed classification verdict
            
        Returns:
            True if VMS routing should proceed
        """
        return classification == "single_resource"
    
    def validate_supplier_count(self, count: int) -> str:
        """
        Validate supplier count against rules (ATS9).
        
        Args:
            count: Number of suppliers in longlist
            
        Returns:
            Validation result: 'valid', 'invalid_low', 'invalid_high'
        """
        if count < 3:
            return "invalid_low"
        elif 3 <= count <= 6:
            return "valid"
        else:
            return "invalid_high"
    
    def validate_supplier_count_with_tol4(self, supplier_count: int) -> dict[str, Any]:
        """
        Validate supplier count via TOL4 adapter (ATS9).
        
        Invokes the TOL4 longlist validation adapter to enforce the 3-6
        supplier count rule and returns full validation result with rule snapshot.
        
        Args:
            supplier_count: Number of suppliers in the longlist
            
        Returns:
            Validation result dictionary from TOL4 adapter
        """
        return self.tol4_adapter.validate_supplier_count(supplier_count)
    
    def validate_lock_preconditions(
        self,
        validation_result: str,
        citation_complete: bool
    ) -> tuple[bool, str]:
        """
        Validate lock preconditions (ATS11 guards).
        
        Args:
            validation_result: Latest supplier-count validation result
            citation_complete: Whether all recommended suppliers have citations
            
        Returns:
            Tuple of (can_lock, reason)
        """
        if validation_result != "valid":
            return (False, f"Supplier count validation result is {validation_result}, must be valid")
        
        if not citation_complete:
            return (False, "Not all recommended suppliers have citations")
        
        return (True, "")
    
    def validate_dispatch_preconditions(self, has_locked_longlist: bool) -> tuple[bool, str]:
        """
        Validate dispatch preconditions (ATS12 guards).
        
        Args:
            has_locked_longlist: Whether case has a locked longlist
            
        Returns:
            Tuple of (can_dispatch, reason)
        """
        if not has_locked_longlist:
            return (False, "Case does not have a locked longlist")
        
        return (True, "")
    
    def route_single_resource_case(
        self,
        case_id: int,
        case_number: str,
        classification_result: dict[str, Any],
        confirmed_attributes: dict[str, Any]
    ) -> VMSHandoff:
        """
        Route single-resource case to VMS via TOL5 adapter (ATS4).
        
        Args:
            case_id: Case identifier
            case_number: Human-readable case number
            classification_result: Classification verdict and metadata
            confirmed_attributes: Confirmed attributes from extraction review
            
        Returns:
            Created VMSHandoff record
        """
        if self.session is None:
            raise ValueError("Session required for VMS routing")
        
        # Invoke TOL5 adapter
        handoff_result = self.tol5_adapter.handoff_to_vms(
            case_id=case_id,
            case_number=case_number,
            classification_result=classification_result,
            confirmed_attributes=confirmed_attributes
        )
        
        # Create VMS handoff record
        vms_handoff = VMSHandoff(
            case_id=case_id,
            vms_reference_id=handoff_result["vms_reference_id"],
            handoff_status=handoff_result["handoff_status"],
            request_snapshot=handoff_result["request_snapshot"],
            requirement_tags="REQ-INT-001"
        )
        
        self.session.add(vms_handoff)
        self.session.flush()
        
        return vms_handoff
    
    def retrieve_evidence(
        self,
        case_id: int,
        confirmed_attributes: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Retrieve historical supplier evidence via TOL2 adapter (ATS5).
        
        Coordinates evidence retrieval from supplier knowledge base and
        normalizes results for storage by evidence service.
        
        Args:
            case_id: Case identifier
            confirmed_attributes: Confirmed attributes from extraction review
            
        Returns:
            List of normalized evidence dictionaries
        """
        # Invoke TOL2 adapter
        raw_evidence = self.tol2_adapter.query_historical_evidence(case_id, confirmed_attributes)
        
        # Normalize evidence results
        normalized_evidence = []
        for item in raw_evidence:
            normalized_evidence.append({
                "supplier_code": item["supplier_code"],
                "supplier_name": item["supplier_name"],
                "evidence_type": item["evidence_type"],
                "external_ref": item["external_ref"],
                "citation_label": item["citation_label"],
                "citation_ref": item["citation_ref"],
                "evidence_summary": item["evidence_summary"],
                "evidence_found": item.get("evidence_found", True),
                "service_domain": item.get("service_domain", ""),
                "completion_date": item.get("completion_date"),
                "signed_date": item.get("signed_date")
            })
        
        return normalized_evidence
    
    def resolve_mappings(
        self,
        case_id: int,
        confirmed_attributes: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Resolve panel and functional-group mappings via TOL3 adapter (ATS6).
        
        Coordinates panel/functional-group lookup from enterprise master data
        and returns mapping candidates for storage by mapping service.
        
        Args:
            case_id: Case identifier
            confirmed_attributes: Confirmed attributes from extraction review
            
        Returns:
            List of mapping dictionaries with panel, functional group, and rationale
        """
        # Invoke TOL3 adapter
        mapping_candidates = self.tol3_adapter.query_panel_mappings(case_id, confirmed_attributes)
        
        # Return normalized mapping results
        return mapping_candidates
