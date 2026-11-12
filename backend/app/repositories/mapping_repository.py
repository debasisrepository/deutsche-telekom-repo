"""Mapping Repository - Data access for panel and functional-group mappings."""
from sqlalchemy.orm import Session

from app.models.case_mapping import CaseMapping
from app.models.functional_group import FunctionalGroup
from app.models.panel import Panel


class MappingRepository:
    """Repository for panel and functional-group mapping data access."""

    def __init__(self, session: Session):
        self.session = session

    def get_or_create_panel(self, panel_code: str, panel_name: str) -> Panel:
        """Get existing panel or create new one.
        
        Args:
            panel_code: Unique panel code
            panel_name: Panel display name
            
        Returns:
            Panel instance
        """
        panel = self.session.query(Panel).filter_by(panel_code=panel_code).first()
        if not panel:
            panel = Panel(
                panel_code=panel_code,
                panel_name=panel_name,
                requirement_tags="REQ-INT-003"
            )
            self.session.add(panel)
            self.session.flush()
        return panel

    def get_or_create_functional_group(
        self, 
        functional_group_code: str, 
        functional_group_name: str
    ) -> FunctionalGroup:
        """Get existing functional group or create new one.
        
        Args:
            functional_group_code: Unique functional group code
            functional_group_name: Functional group display name
            
        Returns:
            FunctionalGroup instance
        """
        fg = self.session.query(FunctionalGroup).filter_by(
            functional_group_code=functional_group_code
        ).first()
        if not fg:
            fg = FunctionalGroup(
                functional_group_code=functional_group_code,
                functional_group_name=functional_group_name,
                requirement_tags="REQ-INT-003"
            )
            self.session.add(fg)
            self.session.flush()
        return fg

    def create_case_mapping(
        self,
        case_id: int,
        panel_id: int,
        functional_group_id: int,
        mapping_status: str,
        rationale_inputs: str | None = None,
        requirement_tags: str | None = None
    ) -> CaseMapping:
        """Create case mapping record.
        
        Args:
            case_id: Case identifier
            panel_id: Panel identifier
            functional_group_id: Functional group identifier
            mapping_status: Mapping status (e.g., proposed, confirmed)
            rationale_inputs: Rationale text
            requirement_tags: Requirement tags
            
        Returns:
            CaseMapping instance
        """
        mapping = CaseMapping(
            case_id=case_id,
            panel_id=panel_id,
            functional_group_id=functional_group_id,
            mapping_status=mapping_status,
            rationale_inputs=rationale_inputs,
            requirement_tags=requirement_tags
        )
        self.session.add(mapping)
        self.session.flush()
        return mapping

    def list_case_mappings(self, case_id: int) -> list[CaseMapping]:
        """List all mappings for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of CaseMapping instances
        """
        return self.session.query(CaseMapping).filter_by(case_id=case_id).all()

    def get_panel_by_id(self, panel_id: int) -> Panel | None:
        """Get panel by ID.
        
        Args:
            panel_id: Panel identifier
            
        Returns:
            Panel instance or None
        """
        return self.session.query(Panel).filter_by(id=panel_id).first()

    def get_functional_group_by_id(self, functional_group_id: int) -> FunctionalGroup | None:
        """Get functional group by ID.
        
        Args:
            functional_group_id: Functional group identifier
            
        Returns:
            FunctionalGroup instance or None
        """
        return self.session.query(FunctionalGroup).filter_by(id=functional_group_id).first()
