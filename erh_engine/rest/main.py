"""
FastAPI REST server exposing the standardized ERH evaluation contract.

Endpoints:
    GET  /v1/health           liveness + version
    POST /v1/evaluate         generic ERH evaluation (the universal entrypoint)
    POST /v1/llm/evaluate     LLM-DR convenience adapter (Phase 1)
    POST /v1/iam/audit        Cloud IAM / CSPM audit adapter (Phase 2)
    POST /v1/ueba/evaluate    UEBA behavioral-drift adapter (Phase 3)

All domain endpoints converge on :func:`erh_engine.engine.evaluate`.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .. import __version__
from ..contracts.schemas import EvaluateRequest, EvaluateResponse
from ..contracts.schemas import HealthResponse
from ..engine import evaluate as run_evaluate
from ..adapters.llm import router as llm_router
from ..adapters.iam_cspm import router as iam_router
from ..adapters.ueba import router as ueba_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="ERH Engine",
        version=__version__,
        description="Universal behavior/logic decision evaluation engine (Ethical Riemann Hypothesis).",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/v1/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        return HealthResponse(version=__version__)

    @app.post("/v1/evaluate", response_model=EvaluateResponse, tags=["core"])
    def evaluate(request: EvaluateRequest) -> EvaluateResponse:
        """Universal ERH evaluation over a batch of domain-agnostic samples."""
        return run_evaluate(request)

    app.include_router(llm_router)
    app.include_router(iam_router)
    app.include_router(ueba_router)

    return app


app = create_app()
