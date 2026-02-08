"""Tests for HuggingFaceEthicalOracle (mock when transformers unavailable)."""

import pytest


def test_oracle_score_returns_float_in_range():
    """Assert score() returns float in [-1, 1] when mock/fallback."""
    try:
        from erh_core.core.oracle import HuggingFaceEthicalOracle
    except ImportError:
        pytest.skip("erh_core.core.oracle unavailable")

    oracle = HuggingFaceEthicalOracle(cache_path=None)
    result = oracle.score("A simple moral scenario.")
    assert isinstance(result, (int, float))
    assert -1.0 <= result <= 1.0


def test_oracle_score_empty_returns_zero():
    """Assert score('') returns 0.0."""
    try:
        from erh_core.core.oracle import HuggingFaceEthicalOracle
    except ImportError:
        pytest.skip("erh_core.core.oracle unavailable")

    oracle = HuggingFaceEthicalOracle(cache_path=None)
    assert oracle.score("") == 0.0
    assert oracle.score("   ") == 0.0


def test_oracle_to_V_mapping():
    """Assert _to_V maps toxicity to [-1, 1] correctly."""
    try:
        from erh_core.core.oracle import HuggingFaceEthicalOracle
    except ImportError:
        pytest.skip("erh_core.core.oracle unavailable")

    oracle = HuggingFaceEthicalOracle(cache_path=None)
    assert oracle._to_V(0.0) == 1.0  # not toxic = ethical
    assert oracle._to_V(1.0) == -1.0  # toxic = unethical
    assert oracle._to_V(0.5) == 0.0  # neutral
