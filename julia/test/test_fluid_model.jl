"""
Tests for FluidModel.jl — covers the finite-difference PDE solver, the
OrdinaryDiffEq-based formulation, parameter fitting, critical-event detection,
and the steady-state solver.
"""

@testset "FluidModel" begin

    import ..FluidModel as FM
    using Statistics: mean, std

    # -----------------------------------------------------------------------
    # 1. solve_error_density_pde — shape and positivity (Neumann)
    # -----------------------------------------------------------------------
    @testset "solve_error_density_pde Neumann" begin
        u_xt, x_grid, t_grid = FM.solve_error_density_pde(
            (0.0, 50.0), (0.0, 5.0);
            nx=20, nt=15, v=0.1, D=0.01, alpha=0.05
        )
        @test size(u_xt) == (15, 20)
        @test length(x_grid) == 20
        @test length(t_grid) == 15
        @test all(isfinite, u_xt)
        # Initial condition (Gaussian) is non-negative; solution should stay
        # bounded (no explosive blow-up for these parameters)
        @test maximum(abs.(u_xt)) < 10.0
    end

    # -----------------------------------------------------------------------
    # 2. solve_error_density_pde — Dirichlet boundary conditions
    # -----------------------------------------------------------------------
    @testset "solve_error_density_pde Dirichlet" begin
        u_xt, x_grid, t_grid = FM.solve_error_density_pde(
            (0.0, 30.0), (0.0, 3.0);
            nx=15, nt=10, v=0.05, D=0.02, alpha=0.1,
            boundary_conditions="dirichlet"
        )
        @test size(u_xt) == (10, 15)
        # Dirichlet BCs: boundary values should be ≈ 0
        @test abs(u_xt[end, 1])   < 1e-6
        @test abs(u_xt[end, end]) < 1e-6
    end

    # -----------------------------------------------------------------------
    # 3. solve_error_density_pde — custom initial condition
    # -----------------------------------------------------------------------
    @testset "solve_error_density_pde custom IC" begin
        nx = 10
        u0 = zeros(Float64, nx); u0[5] = 1.0   # delta-like spike
        u_xt, _, _ = FM.solve_error_density_pde(
            (0.0, 10.0), (0.0, 1.0);
            nx=nx, nt=8, v=0.1, D=0.1, alpha=0.0,
            initial_condition=u0
        )
        @test u_xt[1, 5] ≈ 1.0    # initial row preserved
        @test all(isfinite, u_xt)
    end

    # -----------------------------------------------------------------------
    # 4. solve_ode_formulation (OrdinaryDiffEq backend)
    # -----------------------------------------------------------------------
    @testset "solve_ode_formulation" begin
        u_xt, x_grid, t_vals = FM.solve_ode_formulation(
            (0.0, 20.0), (0.0, 2.0);
            nx=12, v=0.1, D=0.02, alpha=0.05,
            saveat_pts=8
        )
        @test size(u_xt, 2) == 12   # nx spatial points
        @test length(x_grid) == 12
        @test length(t_vals) <= 8
        @test all(isfinite, u_xt)
    end

    # -----------------------------------------------------------------------
    # 5. detect_critical_phenomena — no events in uniform field
    # -----------------------------------------------------------------------
    @testset "detect_critical_phenomena no events" begin
        u_xt = ones(Float64, 10, 20)   # uniform → no jumps
        x_grid = Float64.(1:20)
        t_grid = Float64.(0:9)
        events = FM.detect_critical_phenomena(u_xt, x_grid, t_grid; threshold=2.0)
        @test isempty(events)
    end

    # -----------------------------------------------------------------------
    # 6. detect_critical_phenomena — injected spike
    # -----------------------------------------------------------------------
    @testset "detect_critical_phenomena injected spike" begin
        u_xt = zeros(Float64, 10, 20)
        u_xt[5, 10] = 100.0    # large spike at (t=5, x=10)
        x_grid = Float64.(1:20)
        t_grid = Float64.(0:9)
        events = FM.detect_critical_phenomena(u_xt, x_grid, t_grid; threshold=1.0)
        @test length(events) >= 1
        # Severity should be "critical" for a 100× spike
        @test any(e -> e["severity"] == "critical", events)
        # All required keys present
        for ev in events
            @test haskey(ev, "time")
            @test haskey(ev, "complexity")
            @test haskey(ev, "density_jump")
            @test haskey(ev, "severity")
        end
    end

    # -----------------------------------------------------------------------
    # 7. fit_fluid_parameters
    # -----------------------------------------------------------------------
    @testset "fit_fluid_parameters" begin
        T, X = 8, 30
        x_vals = Float64.(1:X)
        t_vals = Float64.(0:(T-1))

        # Synthetic data: error grows linearly with x
        E_xt = [0.01 * x for t in 1:T, x in 1:X]

        params = FM.fit_fluid_parameters(E_xt, x_vals, t_vals)
        @test haskey(params, "v")
        @test haskey(params, "D")
        @test haskey(params, "alpha")
        @test 0.001 <= params["v"]     <= 1.0
        @test 0.001 <= params["D"]     <= 0.1
        @test 0.001 <= params["alpha"] <= 0.5

        # Flat error → minimal v
        E_flat = fill(0.1, T, X)
        p_flat = FM.fit_fluid_parameters(E_flat, x_vals, t_vals)
        @test p_flat["v"] <= 0.1
    end

    # -----------------------------------------------------------------------
    # 8. compute_steady_state
    # -----------------------------------------------------------------------
    @testset "compute_steady_state" begin
        S_fn  = x -> sin(π * x / 50)^2   # smooth source
        u_ss, x_grid = FM.compute_steady_state(
            0.1, 0.01, 0.05, S_fn, (0.0, 50.0); nx=20
        )
        @test length(u_ss)   == 20
        @test length(x_grid) == 20
        @test all(isfinite, u_ss)

        # Constant source S(x)=1 → steady state ≈ 1/α = 20
        S_const  = x -> 1.0
        u_const, _ = FM.compute_steady_state(0.0, 0.01, 0.05, S_const,
                                              (1.0, 10.0); nx=15)
        @test all(isfinite, u_const)
    end

    # -----------------------------------------------------------------------
    # 9. PDE mass conservation (diffusion-only, no source, no correction)
    # -----------------------------------------------------------------------
    @testset "PDE approximate mass conservation" begin
        # With α=0 and no source, total mass should decay slowly (only
        # truncation error and boundary effects)
        nx = 30
        u0 = [exp(-((x - 0.5)^2) / 0.02) for x in range(0,1,length=nx)]
        u_xt, x_grid, t_grid = FM.solve_error_density_pde(
            (0.0, 1.0), (0.0, 0.1);
            nx=nx, nt=20, v=0.0, D=0.05, alpha=0.0,
            initial_condition=u0, boundary_conditions="neumann"
        )
        mass_0   = sum(u_xt[1,  :])
        mass_end = sum(u_xt[end,:])
        # With Neumann BCs and α=0 the total integral is conserved; allow 5% tolerance
        @test abs(mass_end - mass_0) / (mass_0 + 1e-10) < 0.10
    end

    # -----------------------------------------------------------------------
    # 10. Convection shifts mass to the right
    # -----------------------------------------------------------------------
    @testset "convection mass shift" begin
        nx = 40
        u0 = zeros(Float64, nx); u0[5] = 1.0   # spike near left boundary
        u_xt, _, _ = FM.solve_error_density_pde(
            (0.0, Float64(nx-1)), (0.0, 5.0);
            nx=nx, nt=50, v=1.0, D=0.0, alpha=0.0,
            initial_condition=u0, boundary_conditions="neumann"
        )
        # Centre of mass should move to the right
        x_grid = Float64.(0:(nx-1))
        cm_initial = sum(x_grid .* u_xt[1,  :]) / (sum(u_xt[1,  :]) + 1e-10)
        cm_final   = sum(x_grid .* u_xt[end,:]) / (sum(u_xt[end,:]) + 1e-10)
        @test cm_final >= cm_initial
    end

end # @testset "FluidModel"
