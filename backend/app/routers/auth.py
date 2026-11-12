from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import LoginRequest, LoginResponse, UserResponse
from app.services.auth_service import create_access_token, verify_password

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Authenticate user with email and password.
    Returns JWT access token and user details.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(request.email)
    
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )
    
    return LoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )
