from uuid import UUID

from sqlalchemy.orm import Session

from app.models.panel_match import PanelMatch


class PanelMatchRepository:
    """Repository for PanelMatch CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, panel_match: PanelMatch) -> PanelMatch:
        """Create a new panel match record."""
        self.db.add(panel_match)
        self.db.commit()
        self.db.refresh(panel_match)
        return panel_match

    def get_by_id(self, panel_match_id: UUID) -> PanelMatch | None:
        """Retrieve a panel match by ID."""
        return self.db.query(PanelMatch).filter(PanelMatch.id == panel_match_id).first()

    def get_by_need_id(self, need_id: UUID) -> list[PanelMatch]:
        """Retrieve all panel matches for a given need."""
        return self.db.query(PanelMatch).filter(PanelMatch.need_id == need_id).all()

    def create_batch(self, panel_matches: list[PanelMatch]) -> list[PanelMatch]:
        """Create multiple panel match records in a batch."""
        self.db.add_all(panel_matches)
        self.db.commit()
        for pm in panel_matches:
            self.db.refresh(pm)
        return panel_matches
