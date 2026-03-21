"""Tests for HuggingFace loader (mock/stub path)."""

import numpy as np
import pytest

try:
    from simulation.real_data.huggingface_loader import (
        load_ethics_commonsense,
        load_social_i_qa,
        load_moral_stories,
        text_to_interaction_matrix,
        load_and_build_J,
    )
except ImportError:
    load_ethics_commonsense = None
    load_social_i_qa = None
    load_moral_stories = None
    text_to_interaction_matrix = None
    load_and_build_J = None


@pytest.mark.skipif(load_ethics_commonsense is None, reason="huggingface_loader unavailable")
def test_load_ethics_commonsense_returns_list():
    """load_ethics_commonsense returns list of dicts."""
    rows = load_ethics_commonsense(max_samples=5)
    assert isinstance(rows, list)
    assert len(rows) > 0
    assert "input" in rows[0] or "label" in rows[0]


@pytest.mark.skipif(text_to_interaction_matrix is None, reason="huggingface_loader unavailable")
def test_text_to_interaction_matrix_stub():
    """text_to_interaction_matrix with use_stub returns symmetric matrix."""
    texts = ["Hello", "World", "Test"]
    J = text_to_interaction_matrix(texts, use_stub=True)
    assert J.shape == (3, 3)
    np.testing.assert_allclose(J, J.T)
    assert np.all(np.diag(J) == 0) or np.allclose(np.diag(J), 0)


@pytest.mark.skipif(load_and_build_J is None, reason="huggingface_loader unavailable")
def test_load_and_build_J_returns_tuple():
    """load_and_build_J returns (J, V) with J being a matrix."""
    J, V = load_and_build_J(dataset="ethics_commonsense", max_samples=10)
    assert isinstance(J, np.ndarray)
    assert J.ndim == 2
    assert J.shape[0] == J.shape[1]
    # V may be None for some datasets
    assert V is None or isinstance(V, np.ndarray)
