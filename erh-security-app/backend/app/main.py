from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .core.db import Base, engine
from .routers import analysis, assets, health, ingestion, rules, verify, simulate, settings


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app_settings = get_settings()

    app = FastAPI(
        title="ERH-on-Security API",
        version="0.1.0",
        description=(
            "Proof-of-concept API for mapping GitLab DevSecOps data into the "
            "Ethical Riemann Hypothesis (ERH) framework."
        ),
    )

    # Ensure database schema exists (SQLite PoC; replace with migrations in production).
    Base.metadata.create_all(bind=engine)

    # CORS configuration (open for PoC; tighten for production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(assets.router, prefix="/assets", tags=["assets"])
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
    app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
    app.include_router(rules.router, prefix="/api/v1/rules", tags=["rules"])
    app.include_router(verify.router, prefix="/api/v1/verify", tags=["verify"])
    app.include_router(simulate.router, prefix="/api/v1/simulations", tags=["simulate"])
    app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])

    return app


app = create_app()
