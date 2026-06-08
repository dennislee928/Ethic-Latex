"""
Shared scoring helpers used by adapters.

``ethical_value`` wraps the canonical ``HuggingFaceEthicalOracle`` from
``erh_core`` when transformers/torch are installed, and otherwise falls back to
a deterministic lexical toxicity heuristic so the engine still runs in CI.
"""

from __future__ import annotations

import functools
import re
from typing import Optional

# Small lexical fallback so the engine never hard-depends on transformers.
_TOXIC_TERMS = (
    "kill", "bomb", "weapon", "exploit", "malware", "ransomware", "hate",
    "attack", "steal", "fraud", "suicide", "abuse", "illegal", "bypass",
    "jailbreak", "ignore previous", "disregard", "override safety",
)


@functools.lru_cache(maxsize=1)
def _oracle():
    """Lazily construct the HuggingFace oracle once; None if unavailable."""
    try:
        from erh_core.core.judgement_system import HuggingFaceEthicalOracle

        return HuggingFaceEthicalOracle()
    except Exception:
        return None


def _lexical_value(text: str) -> float:
    """Deterministic [-1, 1] safety score: 1.0 safe, -1.0 unsafe."""
    if not text:
        return 1.0
    lowered = text.lower()
    hits = sum(1 for term in _TOXIC_TERMS if term in lowered)
    # Each hit pushes the score down; saturate at -1.
    return float(max(-1.0, 1.0 - 0.5 * hits))


def ethical_value(text: Optional[str], use_oracle: bool = True) -> float:
    """Return an ethical/safety value V(a) in [-1, 1] for a piece of text."""
    text = text or ""
    if use_oracle:
        oracle = _oracle()
        if oracle is not None:
            try:
                return float(max(-1.0, min(1.0, oracle.score(text))))
            except Exception:
                pass
    return _lexical_value(text)


def text_complexity(text: Optional[str]) -> float:
    """Heuristic decision complexity (>=1) from text structure.

    Combines length (tokens) and the number of imperative/constraint clauses,
    clamped to [1, 100] to match the ERH complexity grid.
    """
    if not text:
        return 1.0
    tokens = len(text.split())
    clauses = len(re.findall(r"[.!?;]|\band\b|\bor\b|\bif\b|\bthen\b", text.lower()))
    raw = 1.0 + tokens / 20.0 + clauses * 2.0
    return float(max(1.0, min(100.0, raw)))
