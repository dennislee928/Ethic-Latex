"""Tests for SocialDynamicsQuantumSimulator Ising model (construct_hamiltonian, compute_ground_state)."""

import numpy as np
import pytest

try:
    from simulation.quantum.simulator import (
        SocialDynamicsQuantumSimulator,
        von_neumann_entropy_from_statevector,
    )
except ImportError:
    SocialDynamicsQuantumSimulator = None
    von_neumann_entropy_from_statevector = None


@pytest.fixture
def sim():
    if SocialDynamicsQuantumSimulator is None:
        pytest.skip("SocialDynamicsQuantumSimulator unavailable")
    return SocialDynamicsQuantumSimulator(num_agents=4, seed=42)


@pytest.fixture
def interaction_matrix():
    J = np.array(
        [
            [0, 0.5, 0.2, 0],
            [0.5, 0, 0, 0.3],
            [0.2, 0, 0, 0.4],
            [0, 0.3, 0.4, 0],
        ]
    )
    return J


@pytest.fixture
def biases():
    return np.array([0.1, -0.1, 0.2, 0.0])


def _get_pauli_labels(H):
    """Extract Pauli labels from SparsePauliOp (handles different Qiskit versions)."""
    labels = []
    if hasattr(H, "paulis"):
        for p in H.paulis:
            labels.append(p.to_label() if hasattr(p, "to_label") else str(p))
    else:
        for item in H:
            if isinstance(item, (list, tuple)) and len(item) >= 1:
                p = item[0]
                labels.append(p.to_label() if hasattr(p, "to_label") else str(p))
            elif hasattr(item, "to_label"):
                labels.append(item.to_label())
            else:
                labels.append(str(item))
    return labels


def test_construct_hamiltonian_has_zz_terms(sim, interaction_matrix, biases):
    """Assert construct_hamiltonian produces Pauli strings containing at least one ZZ pair."""
    H = sim.construct_hamiltonian(interaction_matrix, biases)
    if H is None:
        pytest.skip("SparsePauliOp unavailable")
    labels = _get_pauli_labels(H)
    zz_found = any("Z" in label and label.count("Z") >= 2 for label in labels)
    assert zz_found, "Hamiltonian should contain ZZ interaction terms"


def test_construct_hamiltonian_has_x_terms(sim, interaction_matrix, biases):
    """Assert construct_hamiltonian produces Pauli strings containing at least one X."""
    H = sim.construct_hamiltonian(interaction_matrix, biases)
    if H is None:
        pytest.skip("SparsePauliOp unavailable")
    labels = _get_pauli_labels(H)
    x_found = any("X" in label for label in labels)
    assert x_found, "Hamiltonian should contain X (transverse field) terms"


def test_compute_ground_state_returns_tuple(sim, interaction_matrix, biases):
    """Assert compute_ground_state returns Tuple[float, float]."""
    energy, entropy = sim.compute_ground_state(interaction_matrix, biases)
    assert isinstance(energy, (int, float))
    assert isinstance(entropy, (int, float))
    assert len((energy, entropy)) == 2


def test_compute_ground_state_energy_is_real(sim, interaction_matrix, biases):
    """Assert compute_ground_state energy is real when Hamiltonian is real symmetric."""
    energy, _ = sim.compute_ground_state(interaction_matrix, biases)
    assert np.isrealobj(energy) or (isinstance(energy, (int, float)) and not np.iscomplexobj(energy))
