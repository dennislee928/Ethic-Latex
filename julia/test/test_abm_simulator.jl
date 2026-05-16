"""
Tests for ABMSimulator.jl — covers agent creation, simulation steps,
ERH metric computation, calibration, and the HybridModel integration path.
"""

@testset "ABMSimulator" begin

    using ..ABMSimulator
    import ..ABMSimulator as ABMS
    using Agents: allagents, nv

    # -----------------------------------------------------------------------
    # 1. Simulator creation
    # -----------------------------------------------------------------------
    @testset "create_simulator" begin
        sim = ABMS.create_simulator(num_agents=10, network_topology="small_world", seed=1)
        @test isa(sim, ABMS.ABMSimulatorState)
        @test length(collect(allagents(sim.model))) == 10
        @test sim.network_topology == "small_world"
        @test sim.current_time == 0
        @test isempty(sim.simulation_history)

        # All agents should have valid bias / error_rate values
        agents = collect(allagents(sim.model))
        @test all(a -> 0.0 < a.bias_strength <= 0.3, agents)
        @test all(a -> 0.0 <= a.error_rate <= 1.0, agents)
    end

    # -----------------------------------------------------------------------
    # 2. Action generation
    # -----------------------------------------------------------------------
    @testset "generate_world" begin
        import Random: Xoshiro
        actions = ABMS.generate_world(200; rng=Xoshiro(42))
        @test length(actions) == 200
        @test all(a -> 1.0 <= a.c <= 100.0, actions)
        @test all(a -> 0.0 <= a.V <= 1.0, actions)
        @test all(a -> a.w > 0, actions)
    end

    # -----------------------------------------------------------------------
    # 3. Ethical prime selection
    # -----------------------------------------------------------------------
    @testset "select_ethical_primes" begin
        actions = [ABMS.SimAction(i, Float64(i*5), rand(), 1.0 + Float64(i)/10) for i in 1:20]
        judgments = vcat(trues(10), falses(10))   # first 10 are errors
        primes = ABMS.select_ethical_primes(actions, judgments; importance_quantile=0.9)
        # Only error actions with w >= 90th percentile should be selected
        @test length(primes) <= 10
        @test all(a -> any(b -> b.id == a.id, actions[1:10]), primes)

        # No errors → empty result
        empty_primes = ABMS.select_ethical_primes(actions, falses(20))
        @test isempty(empty_primes)
    end

    # -----------------------------------------------------------------------
    # 4. ERH metric computation
    # -----------------------------------------------------------------------
    @testset "compute_Pi_and_error" begin
        primes = [ABMS.SimAction(i, Float64(i*10), 0.5, 1.0) for i in 1:5]
        Pi_x, B_x, E_x, x_vals = ABMS.compute_Pi_and_error(primes, 100)
        @test length(Pi_x) == 100
        @test length(B_x)  == 100
        @test length(E_x)  == 100
        @test Pi_x[end] == 5.0          # all 5 primes have c ≤ 100
        @test Pi_x[9] == 0.0            # no primes with c ≤ 9 (smallest c=10)
        @test Pi_x[10] == 1.0           # one prime with c = 10
    end

    @testset "analyze_error_growth" begin
        x_vals = collect(1:50)
        E_x    = Float64[0.5 * sqrt(x) for x in x_vals]
        analysis = ABMS.analyze_error_growth(E_x, x_vals)
        @test hasfield(typeof(analysis), :erh_satisfied)
        @test hasfield(typeof(analysis), :estimated_exponent)
        @test analysis.estimated_exponent > 0         # positive growth
        @test isfinite(analysis.estimated_exponent)

        # Nearly zero error → no positive points
        zero_analysis = ABMS.analyze_error_growth(zeros(50), x_vals)
        @test !zero_analysis.erh_satisfied
    end

    # -----------------------------------------------------------------------
    # 5. run_simulation! — smoke test
    # -----------------------------------------------------------------------
    @testset "run_simulation! smoke" begin
        sim = ABMS.create_simulator(num_agents=5, seed=99)
        result = ABMS.run_simulation!(sim;
            num_time_steps  = 3,
            actions_per_step = 50,
            τ               = 0.3,
            X_max           = 20,
            track_erh       = true,
            seed            = 99
        )
        @test haskey(result, "erh_history")
        @test haskey(result, "population_history")
        @test haskey(result, "final_state")
        @test haskey(result, "actions_history")
        @test length(result["population_history"]) == 3
        @test length(result["actions_history"]) == 3
        @test sim.current_time == 2  # 0-indexed; last t = num_time_steps - 1
    end

    # -----------------------------------------------------------------------
    # 6. Population statistics in history
    # -----------------------------------------------------------------------
    @testset "population history contents" begin
        sim = ABMS.create_simulator(num_agents=8, seed=7)
        result = ABMS.run_simulation!(sim; num_time_steps=2, actions_per_step=30,
                                       X_max=10, seed=7)
        for entry in result["population_history"]
            @test haskey(entry, "mean_error_rate")
            @test haskey(entry, "num_agents")
            @test entry["num_agents"] == 8
            @test 0.0 <= entry["mean_error_rate"] <= 1.0
        end
    end

    # -----------------------------------------------------------------------
    # 7. compute_temporal_erh
    # -----------------------------------------------------------------------
    @testset "compute_temporal_erh" begin
        sim = ABMS.create_simulator(num_agents=4, seed=11)
        result = ABMS.run_simulation!(sim; num_time_steps=4, actions_per_step=40,
                                       X_max=20, seed=11)
        terh = ABMS.compute_temporal_erh(sim, result["actions_history"]; τ=0.3, X_max=20)

        @test haskey(terh, "Pi_xt");  @test size(terh["Pi_xt"]) == (4, 20)
        @test haskey(terh, "E_xt");   @test size(terh["E_xt"])  == (4, 20)
        @test haskey(terh, "erh_satisfaction")
        @test 0.0 <= terh["erh_satisfaction"]["satisfaction_rate"] <= 1.0
    end

    # -----------------------------------------------------------------------
    # 8. Calibration
    # -----------------------------------------------------------------------
    @testset "calibrate_erh_parameters" begin
        sim = ABMS.create_simulator(num_agents=5, seed=55)
        result = ABMS.run_simulation!(sim; num_time_steps=4, actions_per_step=60,
                                       X_max=30, seed=55)
        cal = ABMS.calibrate_erh_parameters(result; target_exponent=0.5)
        @test cal["calibrated"] == true
        @test haskey(cal, "satisfaction_rate")
        @test 0.0 <= cal["satisfaction_rate"] <= 1.0
        @test isa(cal["recommendations"], Vector)

        # Without ERH history → not calibrated
        bad = ABMS.calibrate_erh_parameters(Dict{String,Any}("x" => 1))
        @test bad["calibrated"] == false
    end

    # -----------------------------------------------------------------------
    # 9. Simulation summary
    # -----------------------------------------------------------------------
    @testset "get_simulation_summary" begin
        sim = ABMS.create_simulator(num_agents=6, seed=33)
        ABMS.run_simulation!(sim; num_time_steps=2, actions_per_step=20,
                              X_max=10, seed=33)
        s = ABMS.get_simulation_summary(sim)
        @test s["num_agents"] == 6
        @test s["simulation_steps_completed"] == 1
        @test 0.0 <= s["mean_error_rate"] <= 1.0
    end

    # -----------------------------------------------------------------------
    # 10. HybridModel integration smoke test
    # (full hybrid tested via test_abm_simulator.jl per spec)
    # -----------------------------------------------------------------------
    @testset "HybridModel integration smoke" begin
        import ..HybridModel as HM
        model = HM.create_hybrid_model(
            num_agents=5,
            network_topology="ring",
            enable_temporal=true,
            enable_network_dynamics=true,
            enable_fluid_model=false,
            seed=77
        )
        @test isa(model, HM.HybridPsychohistoryModel)
        res = HM.run_hybrid_simulation!(model;
            num_time_steps=2, actions_per_step=30, τ=0.3, X_max=15
        )
        @test haskey(res, "abm_results")
        @test haskey(res, "network_dynamics")
        summary = HM.get_hybrid_summary(model)
        @test summary["num_agents"] == 5
        @test summary["features_enabled"]["temporal"] == true
    end

end # @testset "ABMSimulator"
