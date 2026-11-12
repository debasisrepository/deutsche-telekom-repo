# Multi-stage Dockerfile for Deutsche Telekom IT Procurement Backend
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests
COPY pyproject.toml ./

# Install dependencies stage
FROM base AS dependencies

# ARG for optional dependency groups (default: base only, override for postgres)
ARG INSTALL_SPEC=.

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "$INSTALL_SPEC"

# Runtime stage
FROM base AS runtime

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy entrypoint script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Entrypoint runs migrations and seed, then exec's CMD
ENTRYPOINT ["./docker-entrypoint.sh"]

# Start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
