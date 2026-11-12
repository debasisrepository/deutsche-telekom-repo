"""TOL1 Ingest Adapter - Inbound Channel Normalization"""
from typing import Any


class TOL1IngestAdapter:
    """
    Adapter for normalizing inbound intake across multiple channels.
    Handles: RFP documents, email, phone notes, direct supplier offers.
    """
    
    def normalize_intake(
        self,
        channel: str,
        raw_content: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Normalize raw intake content into standard structure.
        
        Args:
            channel: Inbound channel type (rfp_document, email, phone_note, supplier_offer)
            raw_content: Raw intake data
            
        Returns:
            Normalized intake structure with mandatory and sourced fields
        """
        # For now, pass through the raw content with channel metadata
        # ATS1 normalization step will be enhanced with actual parsing logic
        return {
            "inbound_channel": channel,
            "mandatory_fields": {
                "need_title": raw_content.get("title", ""),
                "business_unit": raw_content.get("business_unit", ""),
                "need_description": raw_content.get("description", "")
            },
            "sourced_fields": {
                "source_artifact_ref": raw_content.get("artifact_ref", ""),
                "source_channel_metadata": {
                    "channel": channel,
                    "submitted_via": raw_content.get("submitted_via", "web")
                }
            },
            "derived_fields": {}
        }
