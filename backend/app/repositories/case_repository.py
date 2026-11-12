"""Case Repository - Data access for need cases"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.need_case import NeedCase


class CaseRepository:
    """Repository for NeedCase aggregate."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, case_id: int) -> NeedCase | None:
        """Get case by ID."""
        return self.session.get(NeedCase, case_id)
    
    def get_by_case_number(self, case_number: str) -> NeedCase | None:
        """Get case by unique case number."""
        stmt = select(NeedCase).where(NeedCase.case_number == case_number)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> list[NeedCase]:
        """Get all cases with pagination."""
        stmt = select(NeedCase).order_by(NeedCase.created_at.desc()).limit(limit).offset(offset)
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def count_all(self) -> int:
        """Count total cases."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(NeedCase)
        result = self.session.execute(stmt)
        return result.scalar() or 0
    
    def get_with_relations(self, case_id: int) -> NeedCase | None:
        """Get case with normalized need, source artifacts, and VMS handoff."""
        stmt = (
            select(NeedCase)
            .options(
                joinedload(NeedCase.normalized_need),
                joinedload(NeedCase.source_artifacts),
                joinedload(NeedCase.vms_handoff)
            )
            .where(NeedCase.id == case_id)
        )
        result = self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    def get_by_workflow_state(
        self,
        workflow_state: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[NeedCase]:
        """Get cases filtered by workflow state with pagination."""
        stmt = (
            select(NeedCase)
            .where(NeedCase.workflow_state == workflow_state)
            .order_by(NeedCase.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def count_by_workflow_state(self, workflow_state: str) -> int:
        """Count cases by workflow state."""
        from sqlalchemy import func
        stmt = (
            select(func.count())
            .select_from(NeedCase)
            .where(NeedCase.workflow_state == workflow_state)
        )
        result = self.session.execute(stmt)
        return result.scalar() or 0
