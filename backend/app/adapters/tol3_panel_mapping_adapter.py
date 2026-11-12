"""TOL3 Panel Mapping Adapter - Enterprise panel and functional-group lookup."""
from typing import Any


class TOL3PanelMappingAdapter:
    """
    Adapter for TOL3 enterprise panel and functional-group lookup system.
    
    Queries enterprise master data to suggest relevant panels and functional groups
    based on case attributes. This is a stub implementation returning sample data.
    
    Stub-to-live implementation seam: Replace query logic with actual TOL3 API calls
    when enterprise integration is available.
    """
    
    def query_panel_mappings(self, case_id: int, confirmed_attributes: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Query enterprise system for relevant panel and functional-group mappings.
        
        Args:
            case_id: Case identifier
            confirmed_attributes: Confirmed attributes from extraction review
            
        Returns:
            List of mapping candidates with panel, functional group, and rationale
        """
        # Query panel mappings based on attribute patterns
        # Handle both nested format (from AGN1) and flat format (from tests)
        service_category_field = confirmed_attributes.get("service_category", "")
        if isinstance(service_category_field, dict):
            service_category = service_category_field.get("value", "")
        else:
            service_category = service_category_field
        
        # Lookup relevant panel/functional-group combinations from enterprise system
        if "cloud" in service_category.lower() or "infrastructure" in service_category.lower():
            return [
                {
                    "panel_code": "PANEL-CLOUD-001",
                    "panel_name": "Cloud Infrastructure & Platform Services",
                    "functional_group_code": "FG-INFRA-001",
                    "functional_group_name": "Infrastructure Modernization",
                    "mapping_status": "proposed",
                    "rationale_inputs": "Service category 'cloud infrastructure' matches panel specialization"
                }
            ]
        elif "security" in service_category.lower():
            return [
                {
                    "panel_code": "PANEL-SEC-002",
                    "panel_name": "Security & Risk Management Services",
                    "functional_group_code": "FG-SEC-001",
                    "functional_group_name": "Cybersecurity Services",
                    "mapping_status": "proposed",
                    "rationale_inputs": "Service category 'security' matches panel specialization"
                }
            ]
        elif "software" in service_category.lower() or "development" in service_category.lower():
            return [
                {
                    "panel_code": "PANEL-APP-003",
                    "panel_name": "Application Development & Integration",
                    "functional_group_code": "FG-APP-001",
                    "functional_group_name": "Custom Application Development",
                    "mapping_status": "proposed",
                    "rationale_inputs": "Service category 'software development' matches panel specialization"
                }
            ]
        else:
            # Default mapping for unmatched categories
            return [
                {
                    "panel_code": "PANEL-GENERAL-999",
                    "panel_name": "General IT Services",
                    "functional_group_code": "FG-GENERAL-999",
                    "functional_group_name": "General Professional Services",
                    "mapping_status": "proposed",
                    "rationale_inputs": "Default mapping for uncategorized service"
                }
            ]
