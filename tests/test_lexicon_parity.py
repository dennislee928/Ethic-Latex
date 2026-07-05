"""Parity tests for the shared ethics lexicon.

The canonical list lives in shared/ethics_lexicon.json. Packaging constraints
force copies (the desktop app bundles src/, the Go gateway embeds its own
file) and embedded fallbacks (frozen sidecar, engine without repo layout).
These tests fail the build whenever any copy drifts from the canonical file.
"""

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_lexicon_copies_identical():
    canonical = _load("shared/ethics_lexicon.json")
    assert _load("desktop/src/lexicon.json") == canonical, (
        "desktop/src/lexicon.json drifted from shared/ethics_lexicon.json"
    )
    assert _load("services/ai-gateway/ethics_lexicon.json") == canonical, (
        "services/ai-gateway/ethics_lexicon.json drifted from shared/ethics_lexicon.json"
    )


def test_sidecar_embedded_fallback_matches():
    canonical = _load("shared/ethics_lexicon.json")
    src = (ROOT / "desktop/sidecar/erh_sidecar.py").read_text(encoding="utf-8")
    harm = ast.literal_eval(re.search(r"HARM_LEXICON = (\[[^\]]+\])", src).group(1))
    safe = ast.literal_eval(re.search(r"SAFE_MARKERS = (\[[^\]]+\])", src).group(1))
    assert harm == canonical["harm_lexicon"]
    assert safe == canonical["safe_markers"]


def test_engine_embedded_fallback_matches():
    canonical = _load("shared/ethics_lexicon.json")
    from erh_engine.adapters import scoring

    assert list(scoring._TOXIC_TERMS) == canonical["toxic_terms"]
    assert list(scoring._REFUSAL_MARKERS) == canonical["refusal_markers"]
