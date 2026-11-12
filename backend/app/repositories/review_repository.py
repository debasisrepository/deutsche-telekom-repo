"""Review Repository - Data access for HITL review records"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.hitl_review import HITLReview


class ReviewRepository:
    """Repository for HITL review data access"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, review_id: int) -> HITLReview | None:
        """Get review by ID"""
        return self.session.get(HITLReview, review_id)
    
    def get_by_case_and_type(
        self,
        case_id: int,
        review_type: str,
        status: str | None = None
    ) -> list[HITLReview]:
        """
        Get reviews for a case by type and optionally status.
        
        Args:
            case_id: Case identifier
            review_type: Type of review (extraction, classification)
            status: Optional status filter (pending, approved, rejected)
            
        Returns:
            List of matching HITLReview records
        """
        stmt = select(HITLReview).where(
            HITLReview.case_id == case_id,
            HITLReview.review_type == review_type
        )
        
        if status is not None:
            stmt = stmt.where(HITLReview.status == status)
        
        stmt = stmt.order_by(HITLReview.created_at.desc())
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_pending_for_case(self, case_id: int) -> list[HITLReview]:
        """Get all pending reviews for a case"""
        stmt = select(HITLReview).where(
            HITLReview.case_id == case_id,
            HITLReview.status == "pending"
        ).order_by(HITLReview.created_at.asc())
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def get_latest_by_case_and_type(
        self,
        case_id: int,
        review_type: str
    ) -> HITLReview | None:
        """Get the most recent review for a case by type"""
        stmt = select(HITLReview).where(
            HITLReview.case_id == case_id,
            HITLReview.review_type == review_type
        ).order_by(HITLReview.created_at.desc()).limit(1)
        
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
