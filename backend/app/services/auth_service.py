"""Authentication service."""
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: Session):
        self.session = session

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password."""
        user = self.session.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_token_for_user(self, user: User) -> str:
        """Create an access token for a user."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        return create_access_token(token_data, expires_delta=timedelta(hours=24))
