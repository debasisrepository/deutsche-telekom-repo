"""Authentication middleware."""
from fastapi import HTTPException, Request, status

from app.core.security import decode_access_token


async def jwt_middleware(request: Request, call_next):
    """
    JWT validation middleware.

    Validates JWT tokens and attaches user info to request state.
    Protected routes should use a dependency that checks request.state.user.
    """
    # Skip auth for public endpoints
    public_paths = {"/health", "/ready", "/api/v1/auth/login", "/docs", "/openapi.json"}
    if request.url.path in public_paths:
        return await call_next(request)

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # For now, allow unauthenticated access
        # TODO: Enforce authentication once frontend is ready
        return await call_next(request)

    token = auth_header.replace("Bearer ", "")

    try:
        payload = decode_access_token(token)
        request.state.user = payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await call_next(request)
