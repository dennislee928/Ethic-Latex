"""
Tests for QuantumWalk.jl

Verifies:
  - State normalization: sum of probabilities ≈ 1.0 at every timestep
  - Coin operators are unitary
  - Shift operator is unitary on the truncated (no-boundary) subspace
  - Quantum walk spreads faster than classical (std ~ O(t) vs O(√t))
  - Cancel culture spread returns valid structure
  - Walk amplitudes satisfy expected distributions (biased coin, symmetry)
"""

using Test
using LinearAlgebra
using Statistics

include(joinpath(@__DIR__, "..", "src", "QuantumWalk.jl"))
using .QuantumWalk

@testset "QuantumWalk" begin

    # -----------------------------------------------------------------------
    @testset "Coin operators are unitary" begin
        H = hadamard_coin()
        @test H * H' ≈ I atol=1e-10
        @test H' * H ≈ I atol=1e-10

        for bias in [0.2, 0.5, 0.7, 0.9]
            C = biased_coin(bias)
            @test C * C' ≈ I atol=1e-10
        end
    end

    # -----------------------------------------------------------------------
    @testset "Full coin operator is block-diagonal unitary" begin
        for n_sites in [5, 10]
            C = build_coin_operator(n_sites, 0.5)
            @test size(C) == (2*n_sites, 2*n_sites)
            @test C * C' ≈ I atol=1e-10
        end
    end

    # -----------------------------------------------------------------------
    @testset "quantum_walk_step — state normalization preserved" begin
        n_sites = 21
        # Initial state: |10, coin=0⟩
        state = zeros(ComplexF64, 2 * n_sites)
        state[10 * 2 + 1] = 1.0 + 0im

        norm_before = sum(abs2, state)
        @test norm_before ≈ 1.0 atol=1e-10

        for _ in 1:15
            state = quantum_walk_step(state, n_sites; coin_bias=0.5)
            norm = sum(abs2, state)
            @test norm ≈ 1.0 atol=1e-8
        end
    end

    # -----------------------------------------------------------------------
    @testset "quantum_walk_propagate — probability distributions sum to 1" begin
        probs, timesteps = quantum_walk_propagate(
            n_sites=31, steps=10, initial_site=15, coin_bias=0.5
        )
        @test size(probs, 1) == 31
        @test size(probs, 2) == 11       # steps + 1
        @test length(timesteps) == 11

        for t in 1:(size(probs, 2))
            total = sum(probs[:, t])
            @test total ≈ 1.0 atol=1e-8
        end

        # Initial distribution: all at initial_site
        @test probs[16, 1] ≈ 1.0 atol=1e-10   # site 15 → 1-indexed = 16
        for i in 1:31
            i != 16 && @test probs[i, 1] ≈ 0.0 atol=1e-10
        end
    end

    # -----------------------------------------------------------------------
    @testset "quantum_walk_propagate — walk spreads outward over time" begin
        probs, _ = quantum_walk_propagate(n_sites=41, steps=15, initial_site=20)
        # std at step 0 should be 0; at step 15 should be > 0
        init_dist = probs[:, 1]
        @test sum(init_dist .> 0.0) == 1

        final_dist = probs[:, end]
        x = collect(0.0:40.0)
        mean_pos = sum(x .* final_dist)
        std_dev  = sqrt(sum((x .- mean_pos) .^ 2 .* final_dist))
        @test std_dev > 1.0  # walk has spread beyond initial site
    end

    # -----------------------------------------------------------------------
    @testset "Quantum walk spreads faster than classical (O(t) vs O(√t))" begin
        n_sites = 61
        steps   = 20

        std_q, _ = diffusion_spread(n_sites=n_sites, steps=steps, classical=false)
        std_c, _ = diffusion_spread(n_sites=n_sites, steps=steps, classical=true, seed=0)

        # Quantum std should be materially larger than classical std
        @test std_q > std_c * 1.5  # quantum: ~O(t), classical: ~O(√t)
    end

    # -----------------------------------------------------------------------
    @testset "diffusion_spread — quantum max_prob < 1 (spread has occurred)" begin
        std_q, max_p = diffusion_spread(n_sites=31, steps=10)
        @test std_q > 0.0
        @test 0.0 < max_p <= 1.0
    end

    # -----------------------------------------------------------------------
    @testset "Biased coin — asymmetric distribution" begin
        # coin_bias=0.9 → strong left-skew → walk drifts left from center
        n_sites = 51
        center  = n_sites ÷ 2
        probs, _ = quantum_walk_propagate(
            n_sites=n_sites, steps=15, initial_site=center, coin_bias=0.9
        )
        final_dist = probs[:, end]
        x = collect(0.0:(n_sites-1))
        mean_pos = sum(x .* final_dist)
        # With strong left bias, center of mass should be left of starting point
        @test mean_pos < center  # drifts toward smaller indices

        # coin_bias=0.1 → strong right-skew → drifts right
        probs_r, _ = quantum_walk_propagate(
            n_sites=n_sites, steps=15, initial_site=center, coin_bias=0.1
        )
        final_r = probs_r[:, end]
        mean_r = sum(x .* final_r)
        @test mean_r > center
    end

    # -----------------------------------------------------------------------
    @testset "simulate_cancel_culture_spread — quantum mode" begin
        result = simulate_cancel_culture_spread(
            n_agents=30, steps=10, initial_infected=1,
            quantum=true, seed=42
        )
        @test haskey(result, "spread_at_step")
        @test haskey(result, "infected_fraction")
        @test haskey(result, "quantum")
        @test result["quantum"] == true

        steps_ret = result["spread_at_step"]
        @test length(steps_ret) == 11   # steps + 1
        # Spread starts at 0 (initial state is localized)
        @test steps_ret[1] ≈ 0.0 atol=1e-6
        # Spread increases over time
        @test steps_ret[end] > steps_ret[1]
        # Infected fraction in [0, 1]
        @test 0.0 <= result["infected_fraction"] <= 1.0
    end

    # -----------------------------------------------------------------------
    @testset "simulate_cancel_culture_spread — classical mode" begin
        result = simulate_cancel_culture_spread(
            n_agents=30, steps=10, initial_infected=1,
            quantum=false, seed=7
        )
        @test result["quantum"] == false
        @test length(result["spread_at_step"]) == 11
        @test 0.0 <= result["infected_fraction"] <= 1.0
    end

    # -----------------------------------------------------------------------
    @testset "simulate_cancel_culture_spread — quantum spreads faster than classical" begin
        n_agents = 50
        steps    = 20

        q_res = simulate_cancel_culture_spread(
            n_agents=n_agents, steps=steps, quantum=true, seed=0
        )
        c_res = simulate_cancel_culture_spread(
            n_agents=n_agents, steps=steps, quantum=false, seed=0
        )

        q_final_std = q_res["spread_at_step"][end]
        c_final_std = c_res["spread_at_step"][end]

        # Quantum walk spreads farther than classical diffusion at same steps
        @test q_final_std > c_final_std
    end

    # -----------------------------------------------------------------------
    @testset "Shift operator structure" begin
        n_sites = 5
        S = build_shift_operator(n_sites)
        @test size(S) == (2*n_sites, 2*n_sites)

        # Each column has at most one non-zero (permutation-like on interior)
        for col in 1:(2*n_sites)
            @test sum(abs.(S[:, col]) .> 1e-10) <= 1
        end
    end

    # -----------------------------------------------------------------------
    @testset "quantum_walk_step vs matrix operator step agree" begin
        n_sites = 11
        init_site = 5
        state = zeros(ComplexF64, 2 * n_sites)
        state[init_site * 2 + 1] = 1.0 + 0im

        # Step via element-wise function
        state_fn = quantum_walk_step(state, n_sites; coin_bias=0.5)

        # Step via explicit matrix operators
        C = build_coin_operator(n_sites, 0.5)
        S = build_shift_operator(n_sites)
        state_mat = S * (C * state)

        @test state_fn ≈ state_mat atol=1e-10
    end

end
