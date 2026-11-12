# Deutsche Telekom Procurement Backend

FastAPI backend for the AI-Enabled Supplier Selection Workflow.

## Prerequisites

- Python 3.11 or higher
- pip

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install .
```

3. Copy environment template (if .env doesn't exist):
```bash
cp dev.env .env
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

## Running Tests

```bash
.venv/bin/python -m pytest tests/ -v
```

## Environment Variables

See `dev.env` for required configuration:
- `DATABASE_URL` - Database connection string (default: `sqlite:///./app.db`)
- `SECRET_KEY` - JWT signing secret (required)
- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins
- `DEBUG` - Enable debug mode (default: `false`)
- `API_PORT` - API server port (default: `9000`)

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:9000/docs
- ReDoc: http://localhost:9000/redoc

## Database Migrations

Create a new migration after model changes:
```bash
alembic revision --autogenerate -m "description of change"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback one migration:
```bash
alembic downgrade -1
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory
│   ├── config.py            # Settings and configuration
│   ├── database.py          # SQLAlchemy engine and session
│   ├── models/              # ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic
│   ├── repositories/        # Data access layer
│   ├── middleware/          # Auth, logging, error handling
│   └── adapters/            # External system integrations
├── alembic/                 # Database migrations
├── tests/                   # Test suite
└── pyproject.toml           # Python dependencies
```
