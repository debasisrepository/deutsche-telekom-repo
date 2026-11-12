#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding database..."
python -m app.seed

echo "Starting application..."
exec "$@"
