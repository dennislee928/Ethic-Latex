"""
    QuantumSimulator — Local quantum simulation for ERH ethical judgment.

    Mirrors simulation/quantum/simulator.py (local simulation only).
    IBM Quantum Runtime / cloud paths remain in cloud.py.

    Key classes:
      - LocalQuantumJudge     : single-qubit Rx gate judgment (1 qubit)
      - AdvancedEthicalCircuit: VQE-style ansatz for social consensus (4 qubits)
      - SocialDynamicsSimulator: Ising Hamiltonian + ground-state solver (4 qubits)
      - MoralHamiltonian       : spin-glass frustration model (4 qubits)
      - AdvancedEthicalEngine  : U3 + Rzz entanglement circuit (variable qubits)

    Gate fidelity choices:
      - All gates are ideal (no noise model); fidelity = 1.0.
      - Rx(θ) with θ = difficulty × π replicates the Qiskit Rx rotation.
      - Bell state: H on qubit 0, CNOT(0→1), then Rx on each qubit.
      - Entangling angle for Rzz: strength × π (same as Python).
      - EfficientSU2 ansatz approximated with alternating Ry + CNOT layers.
      - Ising ZZ coupling via chain of Rz(2J) sandwiched with CNOTs.
"""
module QuantumSimulator

using Yao
using YaoArrayRegister
using LinearAlgebra
using Statistics
using Random

export LocalQuantumJudge, judge_action, entangled_judgment, collapse_wavefunction
export AdvancedEthicalCircuit, run_social_simulation
export SocialDynamicsSimulator, construct_ising_hamiltonian, compute_ground_state,
       run_simulation, measure_social_tension
export MoralHamiltonian, build_conflict_hamiltonian, run_phase_transition_sweep
export AdvancedEthicalEngine, build_social_circuit, run_engine_simulation
export calculate_von_neumann_entropy, von_neumann_entropy_from_statevector
export calculate_coupling_coefficients, calculate_external_field

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

"""
    _rx_gate(θ) -> MatrixBlock

Return Rx(θ) = exp(-i θ/2 X) as a Yao MatrixBlock.
"""
function _rx_gate(θ::Float64)
    c = cos(θ / 2)
    s = sin(θ / 2)
    mat = ComplexF64[c  -im*s; -im*s  c]
    return matblock(mat)
end

"""
    _ry_gate(θ) -> MatrixBlock

Return Ry(θ) = exp(-i θ/2 Y).
"""
function _ry_gate(θ::Float64)
    c = cos(θ / 2)
    s = sin(θ / 2)
    mat = ComplexF64[c  -s; s  c]
    return matblock(mat)
end

"""
    _rz_gate(θ) -> MatrixBlock

Return Rz(θ) = exp(-i θ/2 Z).
"""
function _rz_gate(θ::Float64)
    mat = ComplexF64[exp(-im*θ/2) 0; 0 exp(im*θ/2)]
    return matblock(mat)
end

"""
    _u3_gate(θ, φ, λ) -> MatrixBlock

U3 gate (general single-qubit unitary).
"""
function _u3_gate(θ::Float64, φ::Float64, λ::Float64)
    mat = ComplexF64[
        cos(θ/2)              -exp(im*λ)*sin(θ/2);
        exp(im*φ)*sin(θ/2)     exp(im*(φ+λ))*cos(θ/2)
    ]
    return matblock(mat)
end

"""
    _measure_statevec(sv, n_qubits, shots, rng) -> Dict{String,Int}

Sample `shots` bitstrings from a statevector, return count dict.
"""
function _measure_statevec(sv::AbstractVector{<:Complex}, n_qubits::Int, shots::Int,
                            rng::AbstractRNG)
    probs = abs2.(sv)
    probs ./= sum(probs)  # normalize for numerical safety
    n_outcomes = 2^n_qubits
    counts = Dict{String,Int}()
    cumulative = cumsum(probs)
    for _ in 1:shots
        r = rand(rng)
        idx = searchsortedfirst(cumulative, r)
        idx = min(idx, n_outcomes)
        bits = string(idx - 1, base=2, pad=n_qubits)
        counts[bits] = get(counts, bits, 0) + 1
    end
    return counts
end

# ---------------------------------------------------------------------------
# LocalQuantumJudge
# ---------------------------------------------------------------------------

"""
    LocalQuantumJudge

Single-qubit ethical judgment via Rx rotation.

Circuit: |0⟩ → Rx(θ) → measure, θ = clamp(difficulty,0,1) × π.
Maps |0⟩ → +1 (ethical), |1⟩ → -1 (unethical).
Qubit count: 1.
"""
struct LocalQuantumJudge
    shots::Int
    seed::Union{Int,Nothing}
end

LocalQuantumJudge(; shots::Int=1024, seed=nothing) = LocalQuantumJudge(shots, seed)

function _make_rng(seed::Union{Int,Nothing})
    seed === nothing ? Random.default_rng() : MersenneTwister(seed)
end

"""
    collapse_wavefunction(judge, complexity_amplitudes) -> (α², β²)

Map complexity amplitudes to (P(ethical), P(unethical)).
θ = mean(amplitudes) × π.
"""
function collapse_wavefunction(judge::LocalQuantumJudge,
                                complexity_amplitudes::NTuple{N,Float64}) where N
    difficulty = isempty(complexity_amplitudes) ? 0.5 :
                 clamp(mean(collect(complexity_amplitudes)), 0.0, 1.0)
    θ = difficulty * π
    α² = cos(θ / 2)^2
    return (α², 1.0 - α²)
end

"""
    judge_action(judge, difficulty; shots) -> Float64

Run 1-qubit Rx(θ) circuit and return expectation J ∈ [-1,1].
"""
function judge_action(judge::LocalQuantumJudge, difficulty::Float64;
                      shots::Union{Int,Nothing}=nothing)::Float64
    n = shots === nothing ? judge.shots : shots
    rng = _make_rng(judge.seed)
    θ = clamp(difficulty, 0.0, 1.0) * π

    # Build and apply Rx circuit to |0⟩
    reg = zero_state(1)
    rx_block = put(1, 1 => _rx_gate(θ))
    reg = apply!(reg, rx_block)
    sv = statevec(reg)

    counts = _measure_statevec(sv, 1, n, rng)
    p0 = get(counts, "0", 0) / n
    return 2.0 * p0 - 1.0
end

"""
    entangled_judgment(judge, agent_a_bias, agent_b_bias) -> (J_a, J_b)

Bell state |Φ⁺⟩ = (|00⟩+|11⟩)/√2 with local Rx rotations, then measure.
Circuit (2 qubits): H(0) → CNOT(0,1) → Rx(θ_a,0) → Rx(θ_b,1) → measure.
"""
function entangled_judgment(judge::LocalQuantumJudge,
                             agent_a_bias::Float64,
                             agent_b_bias::Float64)::Tuple{Float64,Float64}
    rng = _make_rng(judge.seed)
    θ_a = clamp(agent_a_bias, -1.0, 1.0) * π / 2
    θ_b = clamp(agent_b_bias, -1.0, 1.0) * π / 2

    reg = zero_state(2)
    # H on qubit 1 (Yao: qubit index 1 = rightmost), CNOT(control=1, target=2)
    bell_circuit = chain(2,
        put(2, 1 => H),
        control(2, 1, 2 => X),
        put(2, 1 => _rx_gate(θ_a)),
        put(2, 2 => _rx_gate(θ_b)),
    )
    reg = apply!(reg, bell_circuit)
    sv = statevec(reg)

    counts = _measure_statevec(sv, 2, judge.shots, rng)
    j_a_vals = Float64[]
    j_b_vals = Float64[]
    for (outcome, cnt) in counts
        # Yao statevec ordering: qubit 1 is LSB
        # bitstring "ab" → qubit1=b, qubit2=a in little-endian
        a_bit = outcome[1]   # first char = qubit 2
        b_bit = outcome[2]   # second char = qubit 1
        a_val = a_bit == '0' ? 1.0 : -1.0
        b_val = b_bit == '0' ? 1.0 : -1.0
        for _ in 1:cnt
            push!(j_a_vals, a_val)
            push!(j_b_vals, b_val)
        end
    end
    j_a = isempty(j_a_vals) ? 0.0 : mean(j_a_vals)
    j_b = isempty(j_b_vals) ? 0.0 : mean(j_b_vals)
    return (j_a, j_b)
end

# ---------------------------------------------------------------------------
# AdvancedEthicalCircuit  (VQE-style EfficientSU2 ansatz approximation)
# ---------------------------------------------------------------------------

"""
    AdvancedEthicalCircuit

VQE-style ansatz for social consensus simulation.

Approximates EfficientSU2 with alternating Ry + CNOT layers.
Default: 4 qubits, 3 repetition layers.
"""
struct AdvancedEthicalCircuit
    n_qubits::Int
    reps::Int
    seed::Union{Int,Nothing}
end

AdvancedEthicalCircuit(; n_qubits::Int=4, reps::Int=3, seed=nothing) =
    AdvancedEthicalCircuit(n_qubits, reps, seed)

"""
    _efficient_su2_params_count(n_qubits, reps) -> Int

Number of free parameters in EfficientSU2(n_qubits, reps) approximation.
Each layer has n_qubits Ry gates; there are reps+1 rotation layers.
"""
function _efficient_su2_params_count(n_qubits::Int, reps::Int)
    return n_qubits * (reps + 1)
end

"""
    _build_efficient_su2(n_qubits, reps, params) -> CompositeBlock

Alternating Ry rotation layers with full CNOT entanglement (linear topology).
"""
function _build_efficient_su2(n_qubits::Int, reps::Int, params::Vector{Float64})
    blocks = []
    param_idx = 1
    for layer in 0:reps
        # Rotation layer
        for q in 1:n_qubits
            θ = params[param_idx]
            param_idx += 1
            push!(blocks, put(n_qubits, q => _ry_gate(θ)))
        end
        # Entanglement layer (linear CNOT chain), skip on last layer
        if layer < reps
            for q in 1:(n_qubits-1)
                push!(blocks, control(n_qubits, q, (q+1) => X))
            end
        end
    end
    return chain(n_qubits, blocks...)
end

"""
    run_social_simulation(circuit; parameters) -> Dict

Run EfficientSU2 ansatz with given parameters (or random if nothing).
Returns stability_index (fraction of shots in all-0 or all-1 consensus).
"""
function run_social_simulation(circuit::AdvancedEthicalCircuit;
                                parameters=nothing)::Dict{String,Any}
    rng = _make_rng(circuit.seed)
    n = circuit.n_qubits
    n_params = _efficient_su2_params_count(n, circuit.reps)

    if parameters === nothing
        params = rand(rng, n_params) .* 2π
    else
        p = vec(Float64.(parameters))
        params = length(p) >= n_params ? p[1:n_params] :
                 [p; rand(rng, n_params - length(p)) .* 2π]
    end

    ansatz = _build_efficient_su2(n, circuit.reps, params)
    reg = zero_state(n)
    reg = apply!(reg, ansatz)
    sv = statevec(reg)

    counts = _measure_statevec(sv, n, 1024, rng)
    return _analyze_consensus(counts, n)
end

function _analyze_consensus(counts::Dict{String,Int}, n_qubits::Int)::Dict{String,Any}
    total = sum(values(counts))
    total == 0 && return Dict{String,Any}("stability_index" => 0.0,
                                           "raw_distribution" => counts)
    zeros_str = repeat("0", n_qubits)
    ones_str  = repeat("1", n_qubits)
    c0 = get(counts, zeros_str, 0)
    c1 = get(counts, ones_str, 0)
    stability = (c0 + c1) / total
    return Dict{String,Any}("stability_index" => stability,
                             "raw_distribution" => counts)
end

# ---------------------------------------------------------------------------
# SocialDynamicsSimulator  (Ising Hamiltonian + ground state)
# ---------------------------------------------------------------------------

"""
    SocialDynamicsSimulator

Physics-informed social consensus using Transverse-Field Ising Hamiltonian.

H = -Σ_{i<j} J_ij Z_i Z_j - Σ_i h_i X_i

Qubit count: num_agents (default 4).
"""
struct SocialDynamicsSimulator
    num_qubits::Int
    reps::Int
    seed::Union{Int,Nothing}
end

SocialDynamicsSimulator(; num_agents::Int=4, reps::Int=3, seed=nothing) =
    SocialDynamicsSimulator(num_agents, reps, seed)

"""
    construct_ising_hamiltonian(sim, interaction_matrix, biases) -> Matrix{ComplexF64}

Build the Ising Hamiltonian matrix for `sim.num_qubits` spins.
Identical sign convention to Python: H = -Σ J_ij ZZ - Σ h_i X.
"""
function construct_ising_hamiltonian(sim::SocialDynamicsSimulator,
                                      interaction_matrix::Matrix{<:Real},
                                      biases::Vector{<:Real})::Matrix{ComplexF64}
    n = sim.num_qubits
    d = 2^n
    H = zeros(ComplexF64, d, d)

    # Pauli matrices
    I2 = ComplexF64[1 0; 0 1]
    X  = ComplexF64[0 1; 1 0]
    Z  = ComplexF64[1 0; 0 -1]

    function kron_single(gate, q, n_q)
        ops = [q == k ? gate : I2 for k in 1:n_q]
        return foldl(kron, ops)
    end

    # ZZ interactions
    n_int = min(n, size(interaction_matrix, 1), size(interaction_matrix, 2))
    for i in 1:n_int, j in (i+1):n_int
        w = (interaction_matrix[i,j] + interaction_matrix[j,i]) / 2.0
        abs(w) < 1e-12 && continue
        Zi = kron_single(Z, i, n)
        Zj = kron_single(Z, j, n)
        H -= w .* (Zi * Zj)
    end

    # Transverse field X
    n_bias = min(n, length(biases))
    for i in 1:n_bias
        b = Float64(biases[i])
        abs(b) < 1e-12 && continue
        Xi = kron_single(X, i, n)
        H -= b .* Xi   # sign: -h X (note Python uses +h X for transverse field)
    end

    return H
end

"""
    compute_ground_state(sim, adjacency_matrix, bias_vector) -> (energy, entropy)

Exact diagonalization to find ground state energy and half-chain von Neumann entropy.
"""
function compute_ground_state(sim::SocialDynamicsSimulator,
                               adjacency_matrix::Matrix{<:Real},
                               bias_vector::Vector{<:Real})::Tuple{Float64,Float64}
    H = construct_ising_hamiltonian(sim, adjacency_matrix, bias_vector)
    # Symmetrize for numerical safety
    H_sym = (H + H') / 2
    evals, evecs = eigen(H_sym)
    energy = real(evals[1])
    gs = evecs[:, 1]

    n = sim.num_qubits
    keep = max(1, n ÷ 2)
    entropy = _half_chain_entropy(gs, n, keep)
    return (energy, entropy)
end

function _half_chain_entropy(statevec::Vector{ComplexF64}, n_qubits::Int,
                               keep::Int)::Float64
    # Reshape into matrix (keep qubits) x (trace-out qubits)
    d_keep = 2^keep
    d_trace = 2^(n_qubits - keep)
    psi = reshape(statevec, d_keep, d_trace)
    rho = psi * psi'
    evals = real.(eigvals(rho))
    evals = clamp.(evals, 1e-15, 1.0)
    return -sum(evals .* log.(evals))
end

"""
    run_simulation(sim, interaction_matrix, biases; params) -> Dict

VQE-style energy estimation. Uses TwoLocal-style ansatz (Ry + CZ layers).
"""
function run_simulation(sim::SocialDynamicsSimulator,
                         interaction_matrix::Matrix{<:Real},
                         biases::Vector{<:Real};
                         params=nothing)::Dict{String,Any}
    rng = _make_rng(sim.seed)
    n = sim.num_qubits
    # TwoLocal(n, "ry", "cz", reps=3): (reps+1)*n params
    n_params = (sim.reps + 1) * n
    if params === nothing
        p = rand(rng, n_params) .* 2π
    else
        p = vec(Float64.(params))
        p = length(p) >= n_params ? p[1:n_params] :
            [p; rand(rng, n_params - length(p)) .* 2π]
    end

    # Build TwoLocal-style circuit and get expectation of Hamiltonian
    H = construct_ising_hamiltonian(sim, interaction_matrix, biases)
    H_sym = (H + H') / 2

    ansatz = _build_twolocal_ry_cz(n, sim.reps, p)
    reg = zero_state(n)
    reg = apply!(reg, ansatz)
    sv = statevec(reg)

    energy = real(sv' * H_sym * sv)
    circuit_depth = sim.reps * (n + (n - 1)) + n  # rotation + entangle layers

    return Dict{String,Any}(
        "social_tension_energy" => energy,
        "is_stable"             => energy < -1.0,
        "circuit_depth"         => circuit_depth,
    )
end

function _build_twolocal_ry_cz(n_qubits::Int, reps::Int, params::Vector{Float64})
    blocks = []
    param_idx = 1
    for layer in 0:reps
        for q in 1:n_qubits
            θ = params[param_idx]; param_idx += 1
            push!(blocks, put(n_qubits, q => _ry_gate(θ)))
        end
        if layer < reps
            for q in 1:(n_qubits-1)
                push!(blocks, control(n_qubits, q, (q+1) => Z))  # CZ gate
            end
        end
    end
    return chain(n_qubits, blocks...)
end

"""
    measure_social_tension(sim, interaction_matrix, biases) -> Float64

Convenience: run_simulation and return energy scalar.
"""
function measure_social_tension(sim::SocialDynamicsSimulator,
                                 interaction_matrix::Matrix{<:Real},
                                 biases::Vector{<:Real})::Float64
    result = run_simulation(sim, interaction_matrix, biases)
    return Float64(result["social_tension_energy"])
end

# ---------------------------------------------------------------------------
# MoralHamiltonian  (spin-glass frustration)
# ---------------------------------------------------------------------------

"""
    MoralHamiltonian

Ising spin-glass Hamiltonian for ethical conflict modeling.

H = -Σ J_ij Z_i Z_j + Σ h X_i

High conflict density → high frustration → phase transition at x_crit.
Qubit count: n_qubits (default 4).
"""
struct MoralHamiltonian
    n_qubits::Int
    seed::Union{Int,Nothing}
end

MoralHamiltonian(; n_qubits::Int=4, seed=nothing) = MoralHamiltonian(n_qubits, seed)

"""
    build_conflict_hamiltonian(mh, conflict_matrix; transverse_field) -> Matrix{ComplexF64}

Build Ising Hamiltonian from moral conflict matrix.
"""
function build_conflict_hamiltonian(mh::MoralHamiltonian,
                                     conflict_matrix::Matrix{<:Real};
                                     transverse_field::Float64=0.1)::Matrix{ComplexF64}
    n = mh.n_qubits
    I2 = ComplexF64[1 0; 0 1]
    X  = ComplexF64[0 1; 1 0]
    Z  = ComplexF64[1 0; 0 -1]

    function kron_single(gate, q)
        ops = [q == k ? gate : I2 for k in 1:n]
        foldl(kron, ops)
    end

    d = 2^n
    H = zeros(ComplexF64, d, d)
    n_int = min(n, size(conflict_matrix, 1), size(conflict_matrix, 2))

    for i in 1:n_int, j in (i+1):n_int
        w = (conflict_matrix[i,j] + conflict_matrix[j,i]) / 2.0
        abs(w) < 1e-12 && continue
        H -= w .* (kron_single(Z, i) * kron_single(Z, j))
    end
    for i in 1:n
        H += transverse_field .* kron_single(X, i)
    end
    return H
end

"""
    run_phase_transition_sweep(mh, conflict_densities; base_strength, shots)
        -> Dict{String,Any}

Sweep conflict density, measuring fidelity (overlap with |0⟩) and coherence.
"""
function run_phase_transition_sweep(mh::MoralHamiltonian,
                                     conflict_densities::Vector{Float64};
                                     base_strength::Float64=0.5,
                                     shots::Int=2048)::Dict{String,Any}
    rng = _make_rng(mh.seed)
    n = mh.n_qubits
    fidelities  = Float64[]
    coherences  = Float64[]
    entropies   = Float64[]

    for ρ in conflict_densities
        J = (rand(rng, n, n) .- 0.5) .* 2
        J = (J + J') / 2
        fill!(view(J, diagind(J)), 0.0)
        J .*= base_strength * ρ

        H = build_conflict_hamiltonian(mh, J)
        H_sym = (H + H') / 2
        evals, evecs = eigen(H_sym)
        gs = evecs[:, 1]

        d = 2^n
        fid = abs2(gs[1])        # overlap with |0...0⟩
        p_last = abs2(gs[d])     # overlap with |1...1⟩
        coherence = fid + p_last

        keep = max(1, n ÷ 2)
        ent = _half_chain_entropy(gs, n, keep)

        push!(fidelities, fid)
        push!(coherences, coherence)
        push!(entropies, ent)
    end

    # Estimate collapse: first density where fidelity < 0.3
    collapse_point = nothing
    idx = findfirst(f -> f < 0.3, fidelities)
    if idx !== nothing
        collapse_point = conflict_densities[idx]
    end

    return Dict{String,Any}(
        "conflict_densities"    => conflict_densities,
        "fidelities"            => fidelities,
        "coherences"            => coherences,
        "von_neumann_entropies" => entropies,
        "collapse_point"        => collapse_point,
    )
end

# ---------------------------------------------------------------------------
# AdvancedEthicalEngine  (U3 + Rzz social entanglement)
# ---------------------------------------------------------------------------

"""
    AdvancedEthicalEngine

High-dimensional ethical Hilbert space engine.

Maps agent empathy/flexibility/resilience to U3 gate angles (Bloch sphere),
social connections to Rzz entanglement angles.

Qubit count: num_agents (variable, caller-specified).
"""
struct AdvancedEthicalEngine
    num_qubits::Int
end

AdvancedEthicalEngine(num_agents::Int) = AdvancedEthicalEngine(num_agents)

"""
    _rzz_block(n_qubits, q1, q2, angle) -> CompositeBlock

Rzz(θ) = exp(-i θ/2 Z⊗Z) = CNOT · Rz(θ) · CNOT.
"""
function _rzz_block(n_qubits::Int, q1::Int, q2::Int, angle::Float64)
    return chain(n_qubits,
        control(n_qubits, q1, q2 => X),
        put(n_qubits, q2 => _rz_gate(angle)),
        control(n_qubits, q1, q2 => X),
    )
end

"""
    build_social_circuit(engine, agent_states, adjacency_matrix)
        -> (circuit, n_used)

Build U3 encoding + Rzz entanglement circuit.
agent_states: Vector of Dicts with keys "theta","phi","lambda" (Float64).
adjacency_matrix: Matrix{Float64} of connection strengths (0-1).
"""
function build_social_circuit(engine::AdvancedEthicalEngine,
                               agent_states::Vector{Dict{String,Float64}},
                               adjacency_matrix::Matrix{<:Real})
    n = min(engine.num_qubits, length(agent_states), size(adjacency_matrix, 1))

    blocks = []
    # Encoding layer: U3 per qubit
    for i in 1:n
        st = agent_states[i]
        θ = get(st, "theta", π/2)
        φ = get(st, "phi", 0.0)
        λ = get(st, "lambda", 0.0)
        push!(blocks, put(n, i => _u3_gate(θ, φ, λ)))
    end

    # Entanglement layer: Rzz for connected pairs
    rows = min(n, size(adjacency_matrix, 1))
    cols = min(n, size(adjacency_matrix, 2))
    for i in 1:rows, j in (i+1):cols
        strength = Float64(adjacency_matrix[i, j])
        strength > 0.1 || continue
        angle = strength * π
        push!(blocks, _rzz_block(n, i, j, angle))
    end

    if isempty(blocks)
        return chain(n), n
    end
    return chain(n, blocks...), n
end

"""
    run_engine_simulation(engine, agent_data, adjacency_matrix; shot_count) -> Dict

Map agent data to Bloch angles, run U3+Rzz circuit, return consensus metrics.
"""
function run_engine_simulation(engine::AdvancedEthicalEngine,
                                agent_data::Vector{Dict{String,Float64}},
                                adjacency_matrix::Matrix{<:Real};
                                shot_count::Int=1024)::Dict{String,Any}
    n = min(engine.num_qubits, length(agent_data), size(adjacency_matrix, 1))
    rng = Random.default_rng()

    states = [Dict{String,Float64}(
        "theta"  => get(a, "empathy", 0.5) * π,
        "phi"    => get(a, "flexibility", 0.5) * 2π,
        "lambda" => get(a, "resilience", 0.5) * π,
    ) for a in agent_data[1:n]]

    circ, n_used = build_social_circuit(engine, states, adjacency_matrix)
    reg = zero_state(n_used)
    reg = apply!(reg, circ)
    sv = statevec(reg)

    counts = _measure_statevec(sv, n_used, shot_count, rng)
    total = sum(values(counts))
    most_freq = argmax(counts)
    coherence = total > 0 ? counts[most_freq] / total : 0.0

    return Dict{String,Any}(
        "consensus_state"  => most_freq,
        "system_coherence" => coherence,
        "raw_counts"       => counts,
    )
end

# ---------------------------------------------------------------------------
# Entropy utilities
# ---------------------------------------------------------------------------

"""
    calculate_von_neumann_entropy(density_matrix) -> Float64

S = -Tr(ρ log ρ) in nats.
"""
function calculate_von_neumann_entropy(density_matrix::Matrix{<:Number})::Float64
    ρ = ComplexF64.(density_matrix)
    evals = real.(eigvals((ρ + ρ') / 2))
    evals = clamp.(evals, 1e-15, 1.0)
    return -sum(evals .* log.(evals))
end

"""
    von_neumann_entropy_from_statevector(statevec; trace_out_indices, n_qubits) -> Float64

Compute Von Neumann entropy of reduced density matrix by tracing out qubits.
trace_out_indices: 1-based qubit indices to trace out (nothing → pure state, returns 0).
"""
function von_neumann_entropy_from_statevector(sv::Vector{<:Complex};
                                               trace_out_indices=nothing,
                                               n_qubits::Union{Int,Nothing}=nothing)::Float64
    trace_out_indices === nothing && return 0.0
    isempty(trace_out_indices) && return 0.0

    nq = n_qubits === nothing ? Int(round(log2(length(sv)))) : n_qubits
    keep_indices = setdiff(1:nq, trace_out_indices)
    isempty(keep_indices) && return 0.0

    d_keep  = 2^length(keep_indices)
    d_trace = 2^length(trace_out_indices)
    psi = reshape(sv, d_keep, d_trace)
    rho = psi * psi'
    evals = real.(eigvals((rho + rho') / 2))
    evals = clamp.(evals, 1e-15, 1.0)
    return -sum(evals .* log.(evals))
end

# ---------------------------------------------------------------------------
# Agent-level coupling/field utilities
# ---------------------------------------------------------------------------

"""
    calculate_coupling_coefficients(agents) -> Matrix{Float64}

Convert agent error rates to coupling matrix J_ij.
agents: Vector of NamedTuples or structs with field `error_rate`.
"""
function calculate_coupling_coefficients(agents::Vector)::Matrix{Float64}
    n = min(length(agents), 16)
    n < 2 && return zeros(1, 1)
    J = zeros(n, n)
    for i in 1:n, j in (i+1):n
        ei = Float64(getfield(agents[i], :error_rate, 0.5))
        ej = Float64(getfield(agents[j], :error_rate, 0.5))
        w = 1.0 / (1.0 + abs(ei - ej))
        J[i,j] = J[j,i] = w
    end
    return J
end

# Helper: getfield with default
getfield(x, f::Symbol, default) = hasproperty(x, f) ? getproperty(x, f) : default

"""
    calculate_external_field(agents) -> Vector{Float64}

Convert agent judgment tendencies to transverse field h_i.
"""
function calculate_external_field(agents::Vector)::Vector{Float64}
    n = min(length(agents), 16)
    n < 1 && return [0.0]
    return [clamp(Float64(getfield(a, :judgment_tendency, 0.0)), -1.0, 1.0) for a in agents[1:n]]
end

end # module QuantumSimulator
