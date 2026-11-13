import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional


class TOL2EvidenceAdapter:
    """
    TOL2 Evidence Adapter stub for historical supplier and project evidence retrieval.

    In a deployed environment, this would connect to the actual TOL2 evidence data source.
    For local development, this stub gracefully degrades and signals unavailability.
    """

    def __init__(self):
        self.available = False

    def query_evidence(
        self,
        need_id: uuid.UUID,
        service_type: Optional[str] = None,
        required_skills: Optional[List[str]] = None,
        business_unit_id: Optional[str] = None,
        panel_filters: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Query TOL2 for historical supplier evidence.

        Returns:
            Dictionary with:
            - available: bool indicating if TOL2 is reachable
            - evidence_items: list of evidence records (empty if unavailable)
            - snapshot_timestamp: when the query was executed
        """
        snapshot_timestamp = datetime.now(UTC)

        if not self.available:
            return {
                "available": False,
                "evidence_items": [],
                "snapshot_timestamp": snapshot_timestamp,
            }

        return {
            "available": True,
            "evidence_items": [],
            "snapshot_timestamp": snapshot_timestamp,
        }
