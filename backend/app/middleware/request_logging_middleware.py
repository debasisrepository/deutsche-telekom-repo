"""Request logging middleware."""
import time
import uuid

from fastapi import Request


async def request_logging_middleware(request: Request, call_next):
    """
    Request logging middleware.

    Logs request/response info with correlation IDs for tracing.
    """
    # Generate or extract correlation ID
    correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    # Log request start
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    time.time() - start_time

    # Add correlation ID to response headers
    response.headers["X-Correlation-Id"] = correlation_id

    # Log request completion (structured logging would go here)
    # print(f"[{correlation_id}] {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")

    return response
