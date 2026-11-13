"""Classification review repository for data access."""
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.classification_review import ClassificationReview


class ClassificationReviewRepository:
    """Repository for ClassificationReview CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, review: ClassificationReview) -> ClassificationReview:
        """Create a new classification review record."""
        self.session.add(review)
        self.session.flush()
        self.session.refresh(review)
        return review

    def get_by_id(self, review_id: UUID) -> ClassificationReview | None:
        """Retrieve a classification review by ID."""
        return self.session.query(ClassificationReview).filter(ClassificationReview.id == review_id).first()

    def get_by_need_id(self, need_id: UUID) -> ClassificationReview | None:
        """Retrieve the latest classification review for a need."""
        return (
            self.session.query(ClassificationReview)
            .filter(ClassificationReview.need_id == need_id)
            .order_by(ClassificationReview.created_at.desc())
            .first()
        )

    def update(self, review: ClassificationReview) -> ClassificationReview:
        """Update an existing classification review record."""
        self.session.flush()
        self.session.refresh(review)
        return review
