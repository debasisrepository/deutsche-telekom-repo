"""Global error handling middleware."""
import uuid

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def error_handler_middleware(request: Request, call_next):
    """
    Global exception handler middleware.

    Catches unhandled exceptions and returns consistent error responses.
    """
    try:
        return await call_next(request)
    except HTTPException:
        # Let FastAPI handle HTTP exceptions normally
        raise
    except RequestValidationError:
        # Let FastAPI handle validation errors normally
        raise
    except Exception:
        # Log the error (structured logging would go here)
        correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))

        # Return generic error without leaking internals
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "correlation_id": correlation_id,
            },
        )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors.

    Returns validation errors in a consistent format.
    """
    correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "correlation_id": correlation_id,
            "errors": exc.errors(),
        },
    )
