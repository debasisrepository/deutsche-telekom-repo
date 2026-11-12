# Deutsche Telekom IT Procurement Supplier Selection Workflow

AI-enabled workflow system for IT procurement from need intake to tender dispatch, with human-in-the-loop review gates, evidence-based supplier ranking, and compliance audit trails.

## Overview

This application implements a complete procurement workflow:
- **Multi-channel intake**: RFP documents, email, phone notes, supplier offers
- **AI-powered extraction**: Structured attribute extraction from unstructured needs
- **Classification**: Single-resource vs. IT-service routing
- **Evidence retrieval**: Historical supplier performance, commissioned SoWs, panel mapping
- **Ranked longlists**: Evidence-grounded supplier recommendations with citation completeness
- **Human review gates**: Extraction and classification approval/correction workflows
- **Supplier adjustments**: Business-unit add/remove with count validation
- **Tender dispatch**: Locked longlist preparation and multi-supplier dispatch tracking

## Prerequisites

- **Python 3.11+** - [Download](https://python.org)
- **Node.js 20.19+ or 22.12+** - [Download](https://nodejs.org)
- **npm** (included with Node.js)
- **Git** (for Windows users: [Git for Windows](https://git-scm.com/download/win) with Git Bash)

## Quick Start

### Local Development (SQLite)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd deutsche-telekom-repo
   ```

2. **Start all services**
   ```bash
   ./start.sh
   ```
   On Windows:
   ```cmd
   start.bat
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:9000
   - API Documentation: http://localhost:9000/docs

4. **Login with default credentials**
   - Email: `admin@example.com`
   - Password: `admin123`

5. **Stop all services**
   ```bash
   ./stop.sh
   ```
   On Windows:
   ```cmd
   stop.bat
   ```

### Running with Docker Compose (SQLite)

Build and start all services in containers:

```bash
docker compose up -d
```

Access the application:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

Stop and remove containers:
```bash
docker compose down
```

### Running with PostgreSQL (Production)

Use the PostgreSQL override for production-like database:

```bash
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d
```

This configuration:
- Runs PostgreSQL 16 in a container
- Configures backend with PostgreSQL connection
- Installs `psycopg[binary]` driver in backend image

## Project Structure

```
deutsche-telekom-repo/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── config.py       # Settings and environment config
│   │   ├── database.py     # Database connection and session
│   │   ├── seed.py         # Database seed script
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── routers/        # API endpoint definitions
│   │   ├── services/       # Business logic layer
│   │   ├── repositories/   # Data access layer
│   │   ├── adapters/       # External system integrations
│   │   └── schemas/        # Pydantic request/response models
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend test suite
│   ├── pyproject.toml      # Python dependencies
│   ├── dev.env             # Local development environment template
│   └── Dockerfile          # Backend container image
│
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── main.tsx        # Application entry point
│   │   ├── App.tsx         # Root component with routing
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── lib/            # Utilities, API client, auth context
│   │   └── types/          # TypeScript type definitions
│   ├── e2e/                # End-to-end tests (Playwright)
│   ├── tests/              # Frontend unit tests
│   ├── package.json        # Node dependencies
│   └── Dockerfile          # Frontend container image
│
├── docker-compose.yml              # Base Docker Compose (SQLite)
├── docker-compose.postgres.yml    # PostgreSQL override
├── shared_config.json              # Shared configuration
├── start.sh / start.bat            # Start all services
├── stop.sh / stop.bat              # Stop all services
└── README.md                       # This file
```

## Development Workflow

### Backend Development

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install .

# Run migrations
alembic upgrade head

# Seed database
python -m app.seed

# Start development server
uvicorn app.main:app --reload --port 9000

# Run tests
pytest tests/ -v

# Lint
ruff check app

# Type check
mypy app --ignore-missing-imports
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run unit tests
npm run test

# Run e2e tests
npx playwright test

# Lint
npm run lint

# Type check
npm run type-check

# Build for production
npm run build
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

Test coverage:
- Unit tests for services and repositories
- Integration tests for API endpoints
- Migration parity tests
- Workflow orchestration tests

### Frontend Tests
```bash
cd frontend
npm run test          # Unit tests
npx playwright test   # E2E tests
```

Test coverage:
- Component unit tests
- Journey tests (intake to dispatch, intake to VMS routing)
- Wireframe compliance tests

## Database

### SQLite (Local Development)
- Database file: `backend/app.db`
- Automatically created on first run
- Suitable for local development and testing

### PostgreSQL (Production)
- Connection string format: `postgresql+psycopg://user:password@host:port/database`
- Set via `DATABASE_URL` environment variable
- Use `docker-compose.postgres.yml` for containerized PostgreSQL

### Migrations

Create new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback one migration:
```bash
alembic downgrade -1
```

## Environment Variables

### Backend (`backend/.env`)
- `DATABASE_URL` - Database connection string (default: SQLite)
- `SECRET_KEY` - JWT secret key (required)
- `CORS_ORIGINS` - Comma-separated allowed origins
- `DEBUG` - Enable debug mode (true/false)
- `API_PORT` - Backend server port (default: 9000)

### Frontend
Frontend configuration is done at build time via Vite. The application uses relative API paths (`/api`) which are proxied during development and routed via nginx in production.

## API Documentation

Interactive API documentation is available when the backend is running:
- **Swagger UI**: http://localhost:9000/docs
- **ReDoc**: http://localhost:9000/redoc
- **OpenAPI Schema**: http://localhost:9000/openapi.json

## Deployment

### Building Images

Backend:
```bash
cd backend
docker build -t telekom-procurement-backend .
```

Frontend:
```bash
cd frontend
docker build -t telekom-procurement-frontend .
```

### Deployment Notes

1. **Environment Variables**: Configure production environment variables for backend
2. **Database**: Use PostgreSQL in production (not SQLite)
3. **Secrets**: Generate strong `SECRET_KEY` for JWT tokens
4. **CORS**: Configure `CORS_ORIGINS` to match your frontend domain
5. **SSL/TLS**: Use reverse proxy (nginx, Traefik) for HTTPS termination
6. **Database Backups**: Implement regular backup strategy for PostgreSQL

## Seed Data

Default credentials for local development:
- **Admin User**: admin@example.com / admin123
- **Reviewer User**: reviewer@example.com / reviewer123
- **Manager User**: manager@example.com / manager123

Sample cases are created covering various workflow states:
- Intake pending and normalized cases
- Extraction pending and approved cases
- Classification pending cases
- VMS-routed cases
- Cases with evidence, mappings, and longlist proposals

## Troubleshooting

### Port Already in Use
The startup script automatically finds available ports starting from 9000 (backend) and 5173 (frontend).

### Database Migration Errors
```bash
cd backend
rm app.db  # Delete database
alembic upgrade head  # Recreate from migrations
python -m app.seed    # Reseed data
```

### Frontend Build Errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Docker Build Issues
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker compose build --no-cache
```

## Contributing

1. Create feature branch from `develop`
2. Make changes with tests
3. Run lint, type-check, and tests
4. Submit pull request to `develop`

## License

Proprietary - Deutsche Telekom IT Procurement
