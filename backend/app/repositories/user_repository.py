
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        stmt = select(User).where(User.email == email)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.session.get(User, user_id)
    
    def create(self, email: str, username: str, hashed_password: str, role: str = "user") -> User:
        """Create a new user."""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            role=role,
            is_active=True
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
