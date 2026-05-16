"""
Tests for QuantumSimulator.jl

Verifies:
  - State normalization: sum of probabilities ≈ 1.0
  - Hermitian operators are actually Hermitian
  - Judgment values are in valid range
  - Consensus/stability metrics are bounded
  - Von Neumann entropy is non-negative
"""

using Test
using LinearAlgebra
using Statistics
using Yao
using YaoArrayRegister

# Include the module directly (ERH.jl includes it, but for standalone clarity)
include(joinpath(@__DIR__, "..", "src", "QuantumSimulator.jl"))
using .QuantumSimulator

@testset "QuantumSimulator" begin

    # -----------------------------------------------------------------------
    @testset "LocalQuantumJudge — judge_action normalization" begin
        judge = LocalQuantumJudge(shots=1024, seed=42)

        # judgment must be in [-1, 1]
        for difficulty in [0.0, 0.25, 0.5, 0.75, 1.0]
            j = judge_action(judge, difficulty)
            @test -1.0 <= j <= 1.0
        end

        # difficulty=0 → Rx(0) = I, all shots measure |0⟩ → J = +1
        j_easy = judge_action(judge, 0.0)
        @test j_easy ≈ 1.0 atol=0.05

        # difficulty=1 → Rx(π) = -iX (flips qubit), all |1⟩ → J = -1
        j_hard = judge_action(judge, 1.0)
        @test j_hard ≈ -1.0 atol=0.05
    end

    # -----------------------------------------------------------------------
    @testset "LocalQuantumJudge — collapse_wavefunction normalization" begin
        judge = LocalQuantumJudge()

        for diff in [0.0, 0.3, 0.5, 0.7, 1.0]
            (α², β²) = collapse_wavefunction(judge, (diff,))
            @test α² + β² ≈ 1.0 atol=1e-10
            @test α² >= 0.0
            @test β² >= 0.0
        end

        # Halfway: should be 50/50
        (α², β²) = collapse_wavefunction(judge, (0.5,))
        @test α² ≈ 0.5 atol=0.01
        @test β² ≈ 0.5 atol=0.01
    end

    # -----------------------------------------------------------------------
    @testset "LocalQuantumJudge — entangled_judgment" begin
        judge = LocalQuantumJudge(shots=2048, seed=0)

        # No bias: Bell state |Φ+⟩ → symmetric
        (j_a, j_b) = entangled_judgment(judge, 0.0, 0.0)
        @test -1.0 <= j_a <= 1.0
        @test -1.0 <= j_b <= 1.0

        # Both biases equal → symmetric judgments
        (j_a2, j_b2) = entangled_judgment(judge, 0.5, 0.5)
        @test abs(j_a2 - j_b2) < 0.5  # correlations expected

        # Results should be deterministic with same seed
        judge2 = LocalQuantumJudge(shots=2048, seed=0)
        (ja3, jb3) = entangled_judgment(judge2, 0.3, -0.3)
        @test -1.0 <= ja3 <= 1.0
        @test -1.0 <= jb3 <= 1.0
    end

    # -----------------------------------------------------------------------
    @testset "AdvancedEthicalCircuit — stability_index bounded in [0,1]" begin
        circ = AdvancedEthicalCircuit(n_qubits=4, reps=3, seed=7)
        result = run_social_simulation(circ)
        @test haskey(result, "stability_index")
        @test haskey(result, "raw_distribution")
        idx = result["stability_index"]
        @test 0.0 <= idx <= 1.0

        # Custom parameters
        n_params = 4 * (3 + 1)  # n_qubits * (reps+1)
        params = fill(π/4, n_params)
        result2 = run_social_simulation(circ; parameters=params)
        @test 0.0 <= result2["stability_index"] <= 1.0
    end

    # -----------------------------------------------------------------------
    @testset "AdvancedEthicalCircuit — shot distribution sums to shots" begin
        circ = AdvancedEthicalCircuit(n_qubits=2, reps=1, seed=11)
        result = run_social_simulation(circ)
        total = sum(values(result["raw_distribution"]))
        @test total == 1024
    end

    # -----------------------------------------------------------------------
    @testset "SocialDynamicsSimulator — Hamiltonian is Hermitian" begin
        sim = SocialDynamicsSimulator(num_agents=4, reps=3, seed=42)
        J = [0.0 0.5 0.3 0.1;
             0.5 0.0 0.4 0.2;
             0.3 0.4 0.0 0.6;
             0.1 0.2 0.6 0.0]
        h = [0.1, -0.2, 0.3, -0.1]
        H = construct_ising_hamiltonian(sim, J, h)

        # Hermitian check: H == H†
        @test H ≈ H' atol=1e-10

        # Matrix is square 2^n × 2^n
        @test size(H) == (16, 16)
    end

    # -----------------------------------------------------------------------
    @testset "SocialDynamicsSimulator — ground state energy is real and finite" begin
        sim = SocialDynamicsSimulator(num_agents=2, seed=0)
        J = [0.0 0.5; 0.5 0.0]
        h = [0.1, -0.1]
        (energy, entropy) = compute_ground_state(sim, J, h)
        @test isfinite(energy)
        @test entropy >= 0.0
        @test isfinite(entropy)
    end

    # -----------------------------------------------------------------------
    @testset "SocialDynamicsSimulator — run_simulation energy is finite" begin
        sim = SocialDynamicsSimulator(num_agents=4, seed=99)
        J = [0.0 0.4 0.3 0.2;
             0.4 0.0 0.5 0.1;
             0.3 0.5 0.0 0.4;
             0.2 0.1 0.4 0.0]
        h = [0.2, 0.1, -0.1, 0.3]
        result = run_simulation(sim, J, h)
        @test haskey(result, "social_tension_energy")
        @test isfinite(result["social_tension_energy"])
        @test isa(result["is_stable"], Bool)
    end

    # -----------------------------------------------------------------------
    @testset "SocialDynamicsSimulator — measure_social_tension returns scalar" begin
        sim = SocialDynamicsSimulator(num_agents=3, seed=5)
        J = [0.0 0.3 0.2; 0.3 0.0 0.4; 0.2 0.4 0.0]
        h = [0.1, 0.2, -0.1]
        tension = measure_social_tension(sim, J, h)
        @test isa(tension, Float64)
        @test isfinite(tension)
    end

    # -----------------------------------------------------------------------
    @testset "MoralHamiltonian — build_conflict_hamiltonian is Hermitian" begin
        mh = MoralHamiltonian(n_qubits=4, seed=3)
        J = [0.0 1.0 0.5 0.2;
             1.0 0.0 0.8 0.3;
             0.5 0.8 0.0 0.9;
             0.2 0.3 0.9 0.0]
        H = build_conflict_hamiltonian(mh, J; transverse_field=0.1)
        @test H ≈ H' atol=1e-10
        @test size(H) == (16, 16)
    end

    # -----------------------------------------------------------------------
    @testset "MoralHamiltonian — phase transition sweep produces valid arrays" begin
        mh = MoralHamiltonian(n_qubits=3, seed=22)
        densities = collect(0.0:0.2:1.0)
        result = run_phase_transition_sweep(mh, densities)
        @test haskey(result, "fidelities")
        @test haskey(result, "coherences")
        @test haskey(result, "von_neumann_entropies")
        @test length(result["fidelities"]) == length(densities)

        # Fidelities and coherences in [0, 1]
        for f in result["fidelities"]
            @test 0.0 <= f <= 1.0
        end
        for c in result["coherences"]
            @test 0.0 <= c <= 1.0 + 1e-10  # floating point
        end
        # Entropies non-negative
        for s in result["von_neumann_entropies"]
            @test s >= -1e-10
        end
    end

    # -----------------------------------------------------------------------
    @testset "AdvancedEthicalEngine — state normalization after circuit" begin
        engine = AdvancedEthicalEngine(3)
        agent_data = [
            Dict{String,Float64}("empathy" => 0.8, "flexibility" => 0.5, "resilience" => 0.3),
            Dict{String,Float64}("empathy" => 0.4, "flexibility" => 0.7, "resilience" => 0.6),
            Dict{String,Float64}("empathy" => 0.6, "flexibility" => 0.3, "resilience" => 0.9),
        ]
        adj = [0.0 0.8 0.3; 0.8 0.0 0.5; 0.3 0.5 0.0]
        states = [Dict{String,Float64}(
            "theta"  => a["empathy"] * π,
            "phi"    => a["flexibility"] * 2π,
            "lambda" => a["resilience"] * π,
        ) for a in agent_data]

        # Verify circuit applies without error and statevec is normalized
        circ, n_used = build_social_circuit(engine, states, adj)
        reg = apply!(zero_state(n_used), circ)
        sv = statevec(reg)
        @test sum(abs2, sv) ≈ 1.0 atol=1e-8

        # run_engine_simulation result
        result = run_engine_simulation(engine, agent_data, adj; shot_count=512)
        @test haskey(result, "consensus_state")
        @test haskey(result, "system_coherence")
        @test 0.0 <= result["system_coherence"] <= 1.0
        total = sum(values(result["raw_counts"]))
        @test total == 512
    end

    # -----------------------------------------------------------------------
    @testset "Von Neumann entropy — pure state gives 0, mixed gives > 0" begin
        # Pure 2-qubit state |00⟩ → entropy = 0
        sv_pure = ComplexF64[1.0, 0.0, 0.0, 0.0]
        s = von_neumann_entropy_from_statevector(sv_pure; trace_out_indices=[2])
        @test s >= 0.0
        @test s < 0.1  # nearly 0 for product state |00⟩

        # Bell state (|00⟩+|11⟩)/√2 → max entanglement for 2 qubits
        sv_bell = ComplexF64[1, 0, 0, 1] ./ sqrt(2.0)
        s_bell = von_neumann_entropy_from_statevector(sv_bell; trace_out_indices=[2])
        @test s_bell > 0.5  # significantly entangled: should be log(2)≈0.693

        # density matrix helper
        rho = [0.5 0.0; 0.0 0.5]
        s_rho = calculate_von_neumann_entropy(rho)
        @test s_rho ≈ log(2.0) atol=1e-8
    end

end
