"""Panel Mapping Service - Coordinates panel and functional-group mapping."""
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.mapping_repository import MappingRepository
from app.services.rules.agn5_rule_engine import AGN5RuleEngine


class PanelMappingService:
    """
    Service for coordinating panel and functional-group mapping.
    
    Uses AGN5 rule engine to invoke TOL3 adapter for mapping candidates,
    then stores mappings via mapping repository.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.agn5_engine = AGN5RuleEngine(session)
        self.mapping_repository = MappingRepository(session)
    
    def store_mappings(
        self,
        case_id: int,
        confirmed_attributes: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Retrieve and store panel/functional-group mappings for a case.
        
        Args:
            case_id: Case identifier
            confirmed_attributes: Confirmed attributes from extraction review
            
        Returns:
            List of stored mapping records with IDs
        """
        # Invoke AGN5 to get mapping candidates from TOL3
        mapping_candidates = self.agn5_engine.resolve_mappings(case_id, confirmed_attributes)
        
        stored_mappings = []
        for candidate in mapping_candidates:
            # Get or create panel and functional group
            panel = self.mapping_repository.get_or_create_panel(
                panel_code=candidate["panel_code"],
                panel_name=candidate["panel_name"]
            )
            
            functional_group = self.mapping_repository.get_or_create_functional_group(
                functional_group_code=candidate["functional_group_code"],
                functional_group_name=candidate["functional_group_name"]
            )
            
            # Create case mapping
            case_mapping = self.mapping_repository.create_case_mapping(
                case_id=case_id,
                panel_id=panel.id,
                functional_group_id=functional_group.id,
                mapping_status=candidate["mapping_status"],
                rationale_inputs=candidate["rationale_inputs"],
                requirement_tags="REQ-INT-003"
            )
            
            stored_mappings.append({
                "id": case_mapping.id,
                "panel_code": panel.panel_code,
                "panel_name": panel.panel_name,
                "functional_group_code": functional_group.functional_group_code,
                "functional_group_name": functional_group.functional_group_name,
                "mapping_status": case_mapping.mapping_status,
                "rationale_inputs": case_mapping.rationale_inputs,
                "created_at": case_mapping.created_at.isoformat()
            })
        
        self.session.commit()
        return stored_mappings
    
    def list_mappings(self, case_id: int) -> list[dict[str, Any]]:
        """
        List all panel/functional-group mappings for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of mapping dictionaries
        """
        mappings = self.mapping_repository.list_case_mappings(case_id)
        
        result = []
        for mapping in mappings:
            panel = self.mapping_repository.get_panel_by_id(mapping.panel_id)
            functional_group = self.mapping_repository.get_functional_group_by_id(mapping.functional_group_id)
            
            result.append({
                "id": mapping.id,
                "panel_code": panel.panel_code if panel else None,
                "panel_name": panel.panel_name if panel else None,
                "functional_group_code": functional_group.functional_group_code if functional_group else None,
                "functional_group_name": functional_group.functional_group_name if functional_group else None,
                "mapping_status": mapping.mapping_status,
                "rationale_inputs": mapping.rationale_inputs,
                "created_at": mapping.created_at.isoformat()
            })
        
        return result
