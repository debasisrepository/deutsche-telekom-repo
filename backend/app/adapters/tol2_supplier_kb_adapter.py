"""TOL2 Supplier Knowledge Base Adapter - Stub for historical evidence retrieval.

This adapter provides a stub-to-live seam for querying historical supplier evidence
from enterprise knowledge bases. The stub implementation returns sample data for
development and testing. Production implementation will call actual TOL2 APIs.

Stub-to-live transition documentation:
- Replace query_historical_evidence() implementation with TOL2 API client
- Maintain the same return structure for normalized evidence results
- Add authentication, retry, and circuit breaker patterns for production
- Log TOL2 API responses for audit trail
"""
from typing import Any


class TOL2SupplierKBAdapter:
    """Adapter for querying historical supplier evidence.
    
    Provides sample evidence data for development and testing.
    Production version will integrate with TOL2 API endpoints.
    """

    def query_historical_evidence(self, case_id: int, need_attributes: dict[str, Any]) -> list[dict[str, Any]]:
        """Query historical supplier evidence based on case attributes.
        
        Args:
            case_id: Case identifier for evidence linkage
            need_attributes: Extracted need attributes for matching (service domain, requirements)
        
        Returns:
            List of evidence dictionaries with supplier, citation, and summary fields
            
        Stub behavior:
            Returns 3 sample evidence items for any query to enable testing of:
            - Evidence retrieval flow
            - Citation linking
            - Evidence-grounding validation
            
        Production behavior:
            Will call TOL2 API with:
            - Service domain matching
            - Requirement tag filtering
            - Recency scoring
            - Supplier reputation weighting
        """
        # Return historical evidence from internal knowledge base
        return [
            {
                "supplier_code": "SUP-CLOUD-001",
                "supplier_name": "CloudTech Solutions GmbH",
                "evidence_type": "historical_order",
                "external_ref": "ORD-2025-1234",
                "citation_label": "Cloud Migration - 2025 Q3",
                "citation_ref": "order/ORD-2025-1234",
                "evidence_summary": "Successfully completed cloud infrastructure migration for similar scope in Q3 2025. Delivered on time with 99.9% uptime SLA compliance.",
                "service_domain": "cloud_infrastructure",
                "completion_date": "2025-09-15",
                "evidence_found": True
            },
            {
                "supplier_code": "SUP-SEC-002",
                "supplier_name": "SecureNet Services AG",
                "evidence_type": "commissioned_sow",
                "external_ref": "SOW-2024-5678",
                "citation_label": "Network Security Assessment - 2024",
                "citation_ref": "sow/SOW-2024-5678",
                "evidence_summary": "Delivered comprehensive security audit with remediation roadmap. Scope included penetration testing and compliance assessment.",
                "service_domain": "network_security",
                "signed_date": "2024-11-20",
                "evidence_found": True
            },
            {
                "supplier_code": "SUP-APP-003",
                "supplier_name": "AppDev Partners GmbH",
                "evidence_type": "historical_order",
                "external_ref": "ORD-2025-9012",
                "citation_label": "Application Development - 2025 Q2",
                "citation_ref": "order/ORD-2025-9012",
                "evidence_summary": "Developed custom enterprise application with agile methodology. Delivered 3 major releases with full documentation.",
                "service_domain": "application_development",
                "completion_date": "2025-06-30",
                "evidence_found": True
            }
        ]
