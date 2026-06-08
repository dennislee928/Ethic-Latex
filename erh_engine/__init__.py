"""
erh_engine — standardized, containerizable service layer over the canonical
ERH algorithm in ``erh_core``.

This package exposes a single evaluation contract (:class:`EvaluateRequest` →
:class:`EvaluateResponse`) over both REST (FastAPI) and gRPC, plus domain
adapters (LLM, IAM/CSPM, UEBA) that convert raw domain data into the generic
:class:`Sample` shape consumed by :func:`erh_engine.engine.evaluate`.

The algorithm itself is NOT reimplemented here: every evaluation funnels into
``erh_core`` (``select_ethical_primes`` → ``compute_Pi_and_error`` →
``check_erh_bound_structured`` / ``analyze_error_growth``).
"""

from .contracts.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    EvaluateParams,
    Sample,
    Curve,
)
from .engine import evaluate

__version__ = "0.1.0"

__all__ = [
    "EvaluateRequest",
    "EvaluateResponse",
    "EvaluateParams",
    "Sample",
    "Curve",
    "evaluate",
    "__version__",
]
