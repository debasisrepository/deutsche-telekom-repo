from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth
from app.routers.api.v1 import (
    evidence,
    intake,
    integrations,
    longlist_proposals,
    longlists,
    niche_research,
    panel_mappings,
    reviews,
    tenders,
    workflows,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context for startup and shutdown."""
    # Startup: seed data in dev environment only
    if settings.environment == "development":
        from app.seed import seed_data
        seed_data()

    yield

    # Shutdown: cleanup if needed


app = FastAPI(
    title="Deutsche Telekom Procurement Workflow API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Liveness probe."""
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    """Readiness probe - checks database connectivity."""
    from app.database import engine
    try:
        with engine.connect():
            pass
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}


# Router registrations
app.include_router(auth.router)
app.include_router(intake.router, prefix="/api/v1/intake", tags=["intake"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["evidence"])
app.include_router(panel_mappings.router, prefix="/api/v1", tags=["panel-mappings"])
app.include_router(niche_research.router, prefix="/api/v1", tags=["niche-research"])
app.include_router(longlist_proposals.router, prefix="/api/v1/longlist-proposals", tags=["longlist-proposals"])
app.include_router(longlists.router, prefix="/api/v1/longlists", tags=["longlists"])
app.include_router(tenders.router, prefix="/api/v1/tenders", tags=["tenders"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
