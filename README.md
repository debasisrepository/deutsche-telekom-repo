# Deutsche Telekom IT Procurement Supplier Selection Workflow

A full-stack procurement workflow application for managing IT services supplier selection, from need intake through tender dispatch.

## Overview

This application converts fragmented, experience-based decision making into a traceable, repeatable, and data-grounded process for IT services procurement. It covers the complete workflow from need intake and classification through supplier longlist generation, governance validation, and tender dispatch.

## Features

- **Need Intake & Classification** (ATS1-ATS3): Multi-channel intake, attribute extraction, need classification
- **VMS Routing** (ATS4): Single-resource needs routed to VMS
- **Evidence & Panel Mapping** (ATS5-ATS6): Historical supplier evidence, panel catalog mapping
- **Niche Research** (ATS7): Governed research for coverage gaps
- **Longlist Proposal** (ATS8): Ranked supplier proposals with citations
- **Governance & Validation** (ATS9-ATS11): Count validation, adjustments, immutable locks
- **Tender Dispatch** (ATS12): Multi-supplier tender distribution with retry
- **Audit Trail**: Complete immutable audit logging for compliance

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI, SQLAlchemy (sync), Alembic migrations
- **Frontend**: React 18 with TypeScript, Vite, IBM Carbon Design System
- **Database**: SQLite (local dev), PostgreSQL (production)
- **Testing**: pytest (backend), vitest (frontend), Playwright (E2E)

## Prerequisites

### Local Development
- **Python**: 3.11 or higher
- **Node.js**: 20.19 or higher (matching frontend engines requirement)
- **npm**: Latest version (comes with Node.js)

### Docker Deployment (Optional)
- **Docker**: Latest version
- **Docker Compose**: v2.0 or higher

## Setup

### Option 1: Local Development (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd deutsche-telekom-repo
   ```

2. **Start the application**
   ```bash
   # macOS/Linux
   ./start.sh

   # Windows (requires Git Bash)
   start.bat
   ```

   The start script will:
   - Check prerequisites (Python 3.11+, Node 20.19+)
   - Create Python virtual environment
   - Install backend dependencies
   - Run database migrations
   - Seed sample data
   - Start backend on available port (default 9000)
   - Install frontend dependencies
   - Start frontend on available port (default 5173)
   - Print URLs and default credentials

3. **Access the application**
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:9000
   - **API Documentation**: http://localhost:9000/docs

4. **Stop the application**
   ```bash
   # macOS/Linux
   ./stop.sh

   # Windows
   stop.bat
   ```

### Option 2: Docker with SQLite

```bash
# Build and start services
docker compose up --build

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:9000
```

### Option 3: Docker with PostgreSQL

```bash
# Build and start services with PostgreSQL
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up --build

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:9000
```

## Default Credentials

After starting the application, log in with these credentials:

- **Email**: `procurement.reviewer@telekom.de`
- **Password**: `Review-pass-1`

Additional test users are available in the seed data with different roles.

## Development

### Backend

```bash
cd backend

# Create virtual environment (if not already created)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install .

# Install development dependencies
pip install .[dev]

# Run linting
ruff check app

# Run type checking
mypy app --ignore-missing-imports

# Run tests
pytest

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Seed database
python -m app.seed
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run linting
npm run lint

# Run type checking
npx tsc --noEmit

# Run unit tests
npm run test

# Build for production
npm run build

# Preview production build
npm run preview
```

### End-to-End Tests

```bash
cd frontend

# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npx playwright test

# Run specific test file
npx playwright test e2e/smoke_login.spec.ts

# Run tests in UI mode
npx playwright test --ui
```

## Testing

### Backend Tests

The backend test suite includes:
- **Unit tests**: Service and repository layer tests
- **Integration tests**: API endpoint tests with TestClient
- **Acceptance tests**: Complete journey tests covering workflow scenarios
- **Pipeline tests**: Migration parity and seed idempotency checks

Run all tests:
```bash
cd backend
pytest
```

Run specific test categories:
```bash
# Unit tests only
pytest tests/test_*_service.py

# Integration tests
pytest tests/test_*_integration.py

# Acceptance tests
pytest tests/test_*_acceptance.py

# Pipeline checks
pytest tests/test_pipeline_*.py
```

### Frontend Tests

The frontend test suite includes:
- **Unit tests**: Component tests with React Testing Library
- **E2E tests**: Full workflow tests with Playwright

Run all tests:
```bash
cd frontend
npm run test                    # Unit tests
npx playwright test            # E2E tests
```

## API Documentation

When running locally with `DEBUG=true`, interactive API documentation is available:

- **Swagger UI**: http://localhost:9000/docs
- **ReDoc**: http://localhost:9000/redoc

All API routes are mounted under `/api/v1` prefix:
- `POST /api/v1/intake/needs` - Create need
- `GET /api/v1/intake/needs` - List needs
- `POST /api/v1/reviews/needs/{need_id}/attributes` - Review attributes
- `POST /api/v1/reviews/needs/{need_id}/classification` - Review classification
- `POST /api/v1/integrations/vms/handoffs` - Execute VMS handoff
- And many more...

See `/docs` for complete API reference.

## Deployment

### Environment Variables

Backend environment variables (see `backend/.env.example`):
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT signing secret (MUST change in production)
- `DEBUG` - Enable debug mode (false in production)
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `RATE_LIMIT_ENABLED` - Enable rate limiting
- `ENVIRONMENT` - Environment name (development/staging/production)

Frontend environment variables:
- `VITE_API_URL` - API base URL (optional, defaults to `/api` for same-origin)

### Production Considerations

1. **Database**: Use PostgreSQL instead of SQLite
2. **Secrets**: Change `SECRET_KEY` to a secure random value
3. **Debug**: Set `DEBUG=false`
4. **CORS**: Configure `CORS_ORIGINS` to match your frontend domain
5. **HTTPS**: Run behind a reverse proxy with SSL/TLS
6. **Rate Limiting**: Keep `RATE_LIMIT_ENABLED=true`
7. **Monitoring**: Configure observability sink (ICA Control Tower)

### Docker Deployment

The application includes production-ready Dockerfiles:

**Backend Dockerfile**:
- Multi-stage build for optimal image size
- Runs migrations and seeds on startup via entrypoint
- Supports optional postgres dependency group
- Exposed on port 9000

**Frontend Dockerfile**:
- Multi-stage build with Node builder and nginx runtime
- Nginx serves static assets and proxies `/api` to backend
- Exposed on port 80

**docker-compose.yml**:
- SQLite-based setup for preview/development
- Named volumes for data persistence
- Preview-port annotations for deployment

**docker-compose.postgres.yml**:
- PostgreSQL override for production-like setup
- Health checks for database readiness
- Installs postgres driver dependencies

## Architecture

### Backend Structure
```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings and configuration
│   ├── database.py             # Database engine and session
│   ├── seed.py                 # Seed data script
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── repositories/           # Data access layer
│   ├── services/               # Business logic layer
│   ├── routers/                # API route handlers
│   ├── adapters/               # External system adapters (TOL1-TOL6)
│   ├── middleware/             # Auth, logging, error handling
│   └── core/                   # Security and utilities
├── alembic/                    # Database migrations
├── tests/                      # Test suite
├── pyproject.toml             # Python dependencies
└── Dockerfile                 # Container image
```

### Frontend Structure
```
frontend/
├── src/
│   ├── main.tsx               # Application entry point
│   ├── App.tsx                # Router and layout
│   ├── components/            # Reusable components
│   │   ├── layout/           # Layout components (Sidebar, Header)
│   │   └── auth/             # Auth components (RequireAuth)
│   ├── pages/                # Page components
│   ├── lib/                  # Utilities and API client
│   │   ├── api-client.ts    # Centralized API client
│   │   ├── auth-context.tsx # Authentication context
│   │   └── utils.ts         # Helper functions
│   └── __tests__/           # Component tests
├── e2e/                      # Playwright E2E tests
├── public/                   # Static assets
├── package.json             # Node dependencies
├── vite.config.ts           # Vite configuration
├── nginx.conf.template      # Nginx configuration for Docker
└── Dockerfile               # Container image
```

## Troubleshooting

### Port Already in Use
The start script automatically finds available ports. If you need specific ports, stop other services or use the default port detection.

### Database Migrations
If migrations fail, ensure the database is accessible and try:
```bash
cd backend
alembic upgrade head
```

### Frontend Build Errors
Ensure Node.js version matches requirements:
```bash
node --version  # Should be 20.19+
```

Clear cache and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Permission Denied on Scripts
Make scripts executable:
```bash
chmod +x start.sh stop.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Copyright © 2024 Deutsche Telekom. All rights reserved.

## Support

For issues and questions, please open an issue in the repository or contact the procurement workflow team.
