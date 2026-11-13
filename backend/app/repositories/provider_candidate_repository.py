from uuid import UUID

from sqlalchemy.orm import Session

from app.models.provider_candidate import ProviderCandidate


class ProviderCandidateRepository:
    """Repository for ProviderCandidate CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, candidate: ProviderCandidate) -> ProviderCandidate:
        """Create a new provider candidate record."""
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def get_by_id(self, candidate_id: UUID) -> ProviderCandidate | None:
        """Retrieve a provider candidate by ID."""
        return self.db.query(ProviderCandidate).filter(ProviderCandidate.id == candidate_id).first()

    def get_by_need_id(self, need_id: UUID) -> list[ProviderCandidate]:
        """Retrieve all provider candidates for a given need."""
        return self.db.query(ProviderCandidate).filter(ProviderCandidate.need_id == need_id).all()

    def create_batch(self, candidates: list[ProviderCandidate]) -> list[ProviderCandidate]:
        """Create multiple provider candidate records in a batch."""
        self.db.add_all(candidates)
        self.db.commit()
        for candidate in candidates:
            self.db.refresh(candidate)
        return candidates

    def update(self, candidate: ProviderCandidate) -> ProviderCandidate:
        """Update an existing provider candidate record."""
        self.db.commit()
        self.db.refresh(candidate)
        return candidate
