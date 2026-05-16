"""
Tests for TemporalERH.jl — covers Π(x,t), B(x,t), E(x,t) computation,
baseline variants, track_error_evolution, Mule effect, anomaly detection,
and stochastic perturbation.
"""

@testset "TemporalERH" begin

    import ..TemporalERH as TERH
    using Random: Xoshiro

    # Convenience: build a TAction-like struct compatible with the module
    struct TAct
        id::Int
        c::Float64
        V::Float64
        w::Float64
    end

    # -----------------------------------------------------------------------
    # 1. compute_Pi_temporal
    # -----------------------------------------------------------------------
    @testset "compute_Pi_temporal" begin
        T     = 3
        X_max = 10

        # t=1: one prime at c=5
        # t=2: two primes at c=3 and c=8
        # t=3: empty
        primes_history = [
            [TAct(1, 5.0, 0.5, 1.0)],
            [TAct(2, 3.0, 0.4, 1.0), TAct(3, 8.0, 0.6, 1.0)],
            TAct[]
        ]

        Pi_xt = TERH.compute_Pi_temporal(primes_history, T, X_max)
        @test size(Pi_xt) == (T, X_max)
        @test Pi_xt[1, 5]  == 1.0   # one prime with c ≤ 5 at t=1
        @test Pi_xt[1, 4]  == 0.0   # no prime with c ≤ 4 at t=1
        @test Pi_xt[2, 8]  == 2.0   # two primes with c ≤ 8 at t=2
        @test Pi_xt[2, 2]  == 0.0   # no prime with c ≤ 2 at t=2
        @test Pi_xt[3, 10] == 0.0   # empty at t=3
    end

    # -----------------------------------------------------------------------
    # 2. compute_baseline_temporal — all variants
    # -----------------------------------------------------------------------
    @testset "compute_baseline_temporal" begin
        T, X = 4, 20
        for bt in ("prime_theorem", "linear", "logarithmic_integral", "power_law")
            B = TERH.compute_baseline_temporal(T, X; baseline_type=bt)
            @test size(B) == (T, X)
            @test all(b -> b >= 0, B)
        end

        # Time-dependent drift increases values over time
        B_static = TERH.compute_baseline_temporal(10, 20; time_dependent=false)
        B_drift  = TERH.compute_baseline_temporal(10, 20; time_dependent=true)
        @test B_drift[10, 10] >= B_drift[1, 10]   # later times have higher baseline
    end

    # -----------------------------------------------------------------------
    # 3. compute_E_temporal
    # -----------------------------------------------------------------------
    @testset "compute_E_temporal" begin
        T, X = 5, 15
        Pi = ones(Float64, T, X)
        B  = 0.5 .* ones(Float64, T, X)
        E  = TERH.compute_E_temporal(Pi, B, T, X)
        @test size(E) == (T, X)
        @test all(e -> e ≈ 0.5, E)

        # Zero Pi → negative error
        E2 = TERH.compute_E_temporal(zeros(T, X), B, T, X)
        @test all(e -> e ≈ -0.5, E2)
    end

    # -----------------------------------------------------------------------
    # 4. track_error_evolution
    # -----------------------------------------------------------------------
    @testset "track_error_evolution" begin
        T     = 4
        X_max = 15
        # Build synthetic actions
        function make_actions(n, seed)
            rng = Xoshiro(seed)
            [TAct(i, 1.0 + 99rand(rng), rand(rng), 0.5 + rand(rng)) for i in 1:n]
        end
        actions_history = [make_actions(50, 10+t) for t in 1:T]

        # Judge: error if V < 0.4
        judge_fn(a, τ) = a.V < τ

        result = TERH.track_error_evolution(
            actions_history, judge_fn; τ=0.4, time_steps=T, X_max=X_max
        )
        @test haskey(result, "Pi_xt");  @test size(result["Pi_xt"]) == (T, X_max)
        @test haskey(result, "B_xt");   @test size(result["B_xt"])  == (T, X_max)
        @test haskey(result, "E_xt");   @test size(result["E_xt"])  == (T, X_max)
        @test haskey(result, "primes_history")
        @test length(result["primes_history"]) == T
    end

    # -----------------------------------------------------------------------
    # 5. simulate_mule_effect
    # -----------------------------------------------------------------------
    @testset "simulate_mule_effect" begin
        T, X = 6, 20
        E_xt = zeros(Float64, T, X)
        # Set some non-zero baseline so the mule multiplier has something to amplify
        E_xt[3, :] .= 2.0

        E_mod = TERH.simulate_mule_effect(E_xt, 3; mule_strength=3.0,
                                           mule_complexity_range=(8, 15), seed=5)
        @test size(E_mod) == (T, X)
        # The mule time row should differ from the original
        @test !all(E_mod[3, :] .== E_xt[3, :])
        # Earlier rows should be unchanged
        @test E_mod[1, :] == E_xt[1, :]
        @test E_mod[2, :] == E_xt[2, :]

        # mule_time beyond time_steps → no modification
        E_noop = TERH.simulate_mule_effect(E_xt, 99; mule_strength=5.0)
        @test E_noop == E_xt
    end

    # -----------------------------------------------------------------------
    # 6. detect_mule_anomalies
    # -----------------------------------------------------------------------
    @testset "detect_mule_anomalies" begin
        T, X = 5, 10
        E_small = 0.01 .* ones(Float64, T, X)
        no_anomalies = TERH.detect_mule_anomalies(E_small; C=1.0, epsilon=0.1)
        @test isempty(no_anomalies)

        # Inject a large violation at (t=2, x=5)
        E_big = copy(E_small)
        E_big[2, 5] = 1000.0
        anomalies = TERH.detect_mule_anomalies(E_big; C=1.0, epsilon=0.1,
                                                threshold_multiplier=1.5, X_max=X)
        @test length(anomalies) >= 1
        found = filter(a -> a["complexity"] == 5, anomalies)
        @test !isempty(found)
        @test found[1]["violation_ratio"] > 1.5

        # All anomaly dicts have required keys
        for a in anomalies
            @test haskey(a, "time")
            @test haskey(a, "complexity")
            @test haskey(a, "error_magnitude")
            @test haskey(a, "erh_bound")
        end
    end

    # -----------------------------------------------------------------------
    # 7. add_stochastic_perturbation
    # -----------------------------------------------------------------------
    @testset "add_stochastic_perturbation" begin
        T, X = 10, 20
        E_base = zeros(Float64, T, X)
        E_pert = TERH.add_stochastic_perturbation(E_base; noise_scale=0.1,
                                                   correlation_time=2, seed=7)
        @test size(E_pert) == (T, X)
        # Perturbed should differ from original
        @test !all(E_pert .== E_base)
        # Standard deviation of noise ≈ noise_scale (rough check)
        @test std(E_pert) < 0.5   # not unbounded

        # Different seeds give different results
        E2 = TERH.add_stochastic_perturbation(E_base; noise_scale=0.1, seed=99)
        @test E_pert != E2
    end

    # -----------------------------------------------------------------------
    # 8. Round-trip: Pi → B → E consistency
    # -----------------------------------------------------------------------
    @testset "Pi-B-E round-trip" begin
        T, X = 3, 8
        primes_history = [
            [TAct(i, Float64(i), 0.5, 1.0) for i in 1:k]
            for k in [3, 5, 7]
        ]
        Pi = TERH.compute_Pi_temporal(primes_history, T, X)
        B  = TERH.compute_baseline_temporal(T, X)
        E  = TERH.compute_E_temporal(Pi, B, T, X)
        @test all(isfinite, E)
        @test E == Pi .- B
    end

end # @testset "TemporalERH"
