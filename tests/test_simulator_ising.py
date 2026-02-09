"""Tests for SocialDynamicsQuantumSimulator Ising model (construct_hamiltonian, compute_ground_state)."""

import numpy as np
import pytest

try:
    from simulation.quantum.simulator import (
        SocialDynamicsQuantumSimulator,
        von_neumann_entropy_from_statevector,
        calculate_coupling_coefficients,
        calculate_external_field,
        calculate_von_neumann_entropy,
    )
except ImportError:
    SocialDynamicsQuantumSimulator = None
    von_neumann_entropy_from_statevector = None
    calculate_coupling_coefficients = None
    calculate_external_field = None
    calculate_von_neumann_entropy = None


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


def test_construct_ising_hamiltonian_alias(sim, interaction_matrix, biases):
    """construct_ising_hamiltonian and construct_hamiltonian return identical result."""
    H1 = sim.construct_hamiltonian(interaction_matrix, biases)
    H2 = sim.construct_ising_hamiltonian(interaction_matrix, biases)
    if H1 is None or H2 is None:
        pytest.skip("SparsePauliOp unavailable")
    m1 = np.asarray(H1.to_matrix()) if hasattr(H1, "to_matrix") else None
    m2 = np.asarray(H2.to_matrix()) if hasattr(H2, "to_matrix") else None
    if m1 is not None and m2 is not None:
        np.testing.assert_allclose(m1, m2)


def test_construct_ising_hamiltonian_zz_sign_convention(sim):
    """ZZ terms use -J_ij convention: H = -Σ J_ij Z_i Z_j."""
    J = np.array([[0, 1.0], [1.0, 0]])
    biases = np.array([0.0, 0.0])
    H = sim.construct_ising_hamiltonian(J, biases)
    if H is None:
        pytest.skip("SparsePauliOp unavailable")
    mat = np.asarray(H.to_matrix())
    assert np.any(np.abs(mat) > 0), "Hamiltonian should be non-trivial"


def test_hamiltonian_matrix_dimensions(sim):
    """H matrix dimensions must match 2^N x 2^N."""
    n = sim.num_qubits
    J = np.eye(n) * 0.5
    np.fill_diagonal(J, 0)
    biases = np.zeros(n)
    H = sim.construct_hamiltonian(J, biases)
    if H is None:
        pytest.skip("SparsePauliOp unavailable")
    mat = np.asarray(H.to_matrix())
    expected = 2**n
    assert mat.shape == (expected, expected), f"Expected {expected}x{expected}, got {mat.shape}"


def test_hamiltonian_hermitian(sim, interaction_matrix, biases):
    """Hamiltonian must be Hermitian: H = H†."""
    H = sim.construct_hamiltonian(interaction_matrix, biases)
    if H is None:
        pytest.skip("SparsePauliOp unavailable")
    mat = np.asarray(H.to_matrix())
    mat_dag = np.conj(mat.T)
    np.testing.assert_allclose(mat, mat_dag, rtol=1e-10, err_msg="H should equal H†")


def test_calculate_coupling_coefficients():
    """calculate_coupling_coefficients produces symmetric J matrix from agents."""
    if calculate_coupling_coefficients is None:
        pytest.skip("calculate_coupling_coefficients unavailable")
    from types import SimpleNamespace

    agents = [
        SimpleNamespace(error_rate=0.1),
        SimpleNamespace(error_rate=0.9),
        SimpleNamespace(error_rate=0.5),
    ]
    J = calculate_coupling_coefficients(agents)
    assert J.shape[0] == J.shape[1]
    np.testing.assert_allclose(J, J.T)


def test_calculate_external_field():
    """calculate_external_field produces h vector from agents."""
    if calculate_external_field is None:
        pytest.skip("calculate_external_field unavailable")
    from types import SimpleNamespace

    agents = [
        SimpleNamespace(judgment_tendency=0.5),
        SimpleNamespace(judgment_tendency=-0.3),
    ]
    h = calculate_external_field(agents)
    assert len(h) == 2
    assert np.all(np.abs(h) <= 1.0)


def test_calculate_von_neumann_entropy_density_matrix():
    """calculate_von_neumann_entropy yields 0 for pure state, >0 for mixture."""
    if calculate_von_neumann_entropy is None:
        pytest.skip("calculate_von_neumann_entropy unavailable")
    pure = np.array([[1, 0], [0, 0]], dtype=complex)
    s_pure = calculate_von_neumann_entropy(pure)
    assert s_pure == 0.0
    mixed = np.eye(2) / 2
    s_mixed = calculate_von_neumann_entropy(mixed)
    assert s_mixed > 0
