"""
Quantum Judgment: non-binary ethical calculations using quantum mechanics.

Provides QuantumOracle interface and implementations (LocalQuantumJudge,
CloudQuantumJudge) for superposition-based ethical judgments, plus an
extended toolkit covering:

    * Multipartite entangled moral communities (GHZ / Bell / W / cluster)
    * Coined quantum walks on arbitrary belief graphs
    * VQE-style ground-state discovery and J_ij parameter fitting
    * Moral interference (two-slit and multi-narrative superpositions)
    * Noise models, Lindblad open-system evolution
    * Heisenberg (XXZ / XYZ) moral Hamiltonians
    * Topological phases (Kitaev / SSH) with winding-number diagnostics
    * Qiskit / PennyLane backend abstraction layer
"""

from .interface import QuantumOracle
from .simulator import (
    LocalQuantumJudge,
    AdvancedEthicalCircuit,
    SocialDynamicsQuantumSimulator,
    AdvancedEthicalQuantumEngine,
)
from .entangled_communities import (
    bell_pair_state,
    ghz_state,
    w_state,
    cluster_state_1d,
    build_community_state,
    echo_chamber_bridge,
    community_correlation,
    EntangledCommunityNetwork,
)
from .entanglement_metrics import (
    partial_trace,
    partial_transpose,
    concurrence,
    negativity,
    logarithmic_negativity,
    purity,
    linear_entropy,
    von_neumann_entropy,
    discord_proxy,
    mutual_information,
)
from .heisenberg import (
    build_xxz_hamiltonian,
    build_xyz_hamiltonian,
    build_heisenberg_sparse_paulis,
    heisenberg_ground_state,
    pauli_matrices,
)
from .lindblad import (
    evolve_unitary,
    evolve_lindblad,
    time_dependent_evolution,
    kraus_amplitude_damping,
    kraus_depolarising,
    apply_kraus,
    lindblad_rhs,
    commutator,
)
from .noise_models import (
    single_qubit_lindblad_ops,
    multi_qubit_depolarising_kraus,
    apply_noise_to_density,
    apply_single_qubit_noise,
    build_aer_noise_model,
)
from .interference import (
    Narrative,
    interference_amplitude,
    measurement_probability,
    societal_measurement,
    two_slit_morality,
    moral_interference_pattern,
)
from .topological import (
    kitaev_bloch_hamiltonian,
    ssh_bloch_hamiltonian,
    winding_number,
    berry_phase,
    kitaev_real_space_hamiltonian,
    classify_phase,
)
from .dynamic_circuits import (
    TimeStep,
    build_dynamic_circuit,
    compile_time_series,
    run_dynamic_evolution,
    pairwise_from_correlation_matrix,
)
from .qml_discovery import (
    hardware_efficient_ansatz,
    expectation,
    vqe_ground_state,
    fit_ising_couplings,
)
from .quantum_walk import (
    quantum_walk_step,
    quantum_walk_propagate,
    diffusion_spread,
    simulate_cancel_culture_spread,
    GraphQuantumWalk,
    classical_walk_on_graph,
    variance_on_cycle,
)
from .backends import (
    QuantumBackend,
    NumpyBackend,
    QiskitBackend,
    PennyLaneBackend,
    select_backend,
    BACKEND_AVAILABILITY,
)

__all__ = [
    # Original
    "QuantumOracle",
    "LocalQuantumJudge",
    "AdvancedEthicalCircuit",
    "SocialDynamicsQuantumSimulator",
    "AdvancedEthicalQuantumEngine",
    # Entangled communities
    "bell_pair_state",
    "ghz_state",
    "w_state",
    "cluster_state_1d",
    "build_community_state",
    "echo_chamber_bridge",
    "community_correlation",
    "EntangledCommunityNetwork",
    # Entanglement metrics
    "partial_trace",
    "partial_transpose",
    "concurrence",
    "negativity",
    "logarithmic_negativity",
    "purity",
    "linear_entropy",
    "von_neumann_entropy",
    "discord_proxy",
    "mutual_information",
    # Heisenberg / XXZ / XYZ
    "build_xxz_hamiltonian",
    "build_xyz_hamiltonian",
    "build_heisenberg_sparse_paulis",
    "heisenberg_ground_state",
    "pauli_matrices",
    # Lindblad / open systems
    "evolve_unitary",
    "evolve_lindblad",
    "time_dependent_evolution",
    "kraus_amplitude_damping",
    "kraus_depolarising",
    "apply_kraus",
    "lindblad_rhs",
    "commutator",
    # Noise models
    "single_qubit_lindblad_ops",
    "multi_qubit_depolarising_kraus",
    "apply_noise_to_density",
    "apply_single_qubit_noise",
    "build_aer_noise_model",
    # Interference
    "Narrative",
    "interference_amplitude",
    "measurement_probability",
    "societal_measurement",
    "two_slit_morality",
    "moral_interference_pattern",
    # Topological
    "kitaev_bloch_hamiltonian",
    "ssh_bloch_hamiltonian",
    "winding_number",
    "berry_phase",
    "kitaev_real_space_hamiltonian",
    "classify_phase",
    # Dynamic circuits
    "TimeStep",
    "build_dynamic_circuit",
    "compile_time_series",
    "run_dynamic_evolution",
    "pairwise_from_correlation_matrix",
    # QML discovery
    "hardware_efficient_ansatz",
    "expectation",
    "vqe_ground_state",
    "fit_ising_couplings",
    # Quantum walk
    "quantum_walk_step",
    "quantum_walk_propagate",
    "diffusion_spread",
    "simulate_cancel_culture_spread",
    "GraphQuantumWalk",
    "classical_walk_on_graph",
    "variance_on_cycle",
    # Backends
    "QuantumBackend",
    "NumpyBackend",
    "QiskitBackend",
    "PennyLaneBackend",
    "select_backend",
    "BACKEND_AVAILABILITY",
]

try:
    from .cloud import CloudQuantumJudge

    __all__.append("CloudQuantumJudge")
except (ImportError, ValueError):
    CloudQuantumJudge = None  # qiskit-ibm-runtime or IBM_QUANTUM_TOKEN
