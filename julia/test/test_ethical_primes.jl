using Test

# Load module under test
include(joinpath(@__DIR__, "../src/EthicalPrimes.jl"))
using .EthicalPrimes

# ---------------------------------------------------------------------------
# Helpers: synthetic action lists
# ---------------------------------------------------------------------------

"""Build n actions with complexity 1..n, weight 1.0, V=0.8, mistake_flag=1."""
function make_mistakes(n::Int)
    [Action(i, 1.0, 0.8, 0.5, 0.3, 1, nothing) for i in 1:n]
end

"""Build a mixed list: first `n_ok` actions are NOT mistakes, rest ARE."""
function make_mixed(n_ok::Int, n_err::Int)
    ok  = [Action(i,     1.0, 0.8, 0.9, 0.1, 0, nothing) for i in 1:n_ok]
    err = [Action(n_ok + i, 2.0, 0.8, 0.5, 0.3, 1, nothing) for i in 1:n_err]
    vcat(ok, err)
end


@testset "EthicalPrimes" begin

    # -----------------------------------------------------------------------
    @testset "Action struct" begin
        a = Action(5, 1.5, 0.7)
        @test a.c == 5
        @test a.w ≈ 1.5
        @test a.V ≈ 0.7
        @test isnothing(a.J)
        @test isnothing(a.delta)
        @test isnothing(a.mistake_flag)
        @test isnothing(a.group)

        a2 = Action(3, 0.5, 0.2, 0.4, 0.2, 1, "groupA")
        @test a2.mistake_flag == 1
        @test a2.group == "groupA"
    end

    # -----------------------------------------------------------------------
    @testset "select_ethical_primes — empty input" begin
        @test select_ethical_primes(Action[]) == Action[]
    end

    @testset "select_ethical_primes — all correct (no mistakes)" begin
        actions = [Action(i, 1.0, 0.9, 0.8, 0.1, 0, nothing) for i in 1:20]
        @test isempty(select_ethical_primes(actions))
    end

    @testset "select_ethical_primes — importance strategy" begin
        # 50 mistakes, importance quantile 0.9 → keep top 10 % = 5
        mistakes = [Action(i, Float64(i), 0.8, 0.5, 0.3, 1, nothing) for i in 1:50]
        primes = select_ethical_primes(mistakes; importance_quantile = 0.9, strategy = :importance)
        @test length(primes) >= 1
        # All returned actions must be mistakes
        @test all(p.mistake_flag == 1 for p in primes)
        # Highest importance first
        @test primes[1].w >= primes[end].w
    end

    @testset "select_ethical_primes — complexity strategy" begin
        mistakes = [Action(i, 1.0, 0.8, 0.5, 0.3, 1, nothing) for i in 1:50]
        primes = select_ethical_primes(mistakes; strategy = :complexity)
        @test !isempty(primes)
        @test all(p.mistake_flag == 1 for p in primes)
    end

    @testset "select_ethical_primes — hybrid strategy" begin
        mistakes = [Action(i, Float64(i), 0.8, 0.5, Float64(i) * 0.01, 1, nothing) for i in 1:50]
        primes = select_ethical_primes(mistakes; strategy = :hybrid)
        @test !isempty(primes)
    end

    @testset "select_ethical_primes — explicit complexity_range" begin
        mistakes = [Action(i, 1.0, 0.8, 0.5, 0.3, 1, nothing) for i in 1:100]
        primes = select_ethical_primes(mistakes; complexity_range = (20, 80))
        @test all(20 <= p.c <= 80 for p in primes)
    end

    @testset "select_ethical_primes — unknown strategy throws" begin
        mistakes = make_mistakes(10)
        @test_throws ArgumentError select_ethical_primes(mistakes; strategy = :bogus)
    end

    # -----------------------------------------------------------------------
    @testset "compute_Pi_and_error — basic shapes" begin
        primes = make_mistakes(50)
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes; X_max = 60)

        @test length(Pi_x)   == 60
        @test length(B_x)    == 60
        @test length(E_x)    == 60
        @test length(x_vals) == 60
        @test x_vals[1] == 1 && x_vals[end] == 60
    end

    @testset "compute_Pi_and_error — Π(x) is non-decreasing" begin
        primes = make_mistakes(40)
        Pi_x, _, _, _ = compute_Pi_and_error(primes; X_max = 50)
        @test all(Pi_x[i] <= Pi_x[i+1] for i in 1:49)
    end

    @testset "compute_Pi_and_error — Π(x) correct count" begin
        primes = [Action(10, 1.0, 0.8, 0.5, 0.3, 1, nothing),
                  Action(20, 1.0, 0.8, 0.5, 0.3, 1, nothing),
                  Action(30, 1.0, 0.8, 0.5, 0.3, 1, nothing)]
        Pi_x, _, _, _ = compute_Pi_and_error(primes; X_max = 40)

        @test Pi_x[9]  == 0
        @test Pi_x[10] == 1
        @test Pi_x[19] == 1
        @test Pi_x[20] == 2
        @test Pi_x[30] == 3
    end

    @testset "compute_Pi_and_error — prime_theorem baseline > 0 for x > 1" begin
        primes = make_mistakes(20)
        _, B_x, _, _ = compute_Pi_and_error(primes; X_max = 20, baseline = :prime_theorem)
        @test B_x[1] == 0.0          # x=1 → set to 0 (log(1)=0 singularity)
        @test all(B_x[2:end] .>= 0)
    end

    @testset "compute_Pi_and_error — linear baseline is linear" begin
        primes = make_mistakes(20)
        alpha = 0.3
        _, B_x, _, x_vals = compute_Pi_and_error(
            primes; X_max = 10, baseline = :linear,
            baseline_params = Dict("alpha" => alpha))
        @test B_x ≈ alpha .* Float64.(x_vals)
    end

    @testset "compute_Pi_and_error — power_law baseline" begin
        primes = make_mistakes(20)
        _, B_x, _, x_vals = compute_Pi_and_error(
            primes; X_max = 10, baseline = :power_law,
            baseline_params = Dict("gamma" => 0.5, "delta" => 1.5))
        @test B_x[5] ≈ 0.5 * 5.0^1.5  atol=1e-10
    end

    @testset "compute_Pi_and_error — empty primes gives zero Π" begin
        Pi_x, _, _, _ = compute_Pi_and_error(Action[]; X_max = 20)
        @test all(Pi_x .== 0)
    end

    @testset "compute_Pi_and_error — unknown baseline throws" begin
        @test_throws ArgumentError compute_Pi_and_error(make_mistakes(5); baseline = :mystery)
    end

    # -----------------------------------------------------------------------
    @testset "compute_error_correction_impact" begin
        actions = make_mixed(10, 20)
        # Indices of mistakes (11..30)
        mistake_indices = collect(11:20)
        impacts = compute_error_correction_impact(actions, mistake_indices)
        @test length(impacts) == length(mistake_indices)
        @test all(0.0 <= v <= 1.0 for v in values(impacts))
    end

    @testset "compute_error_correction_impact — non-mistake index gives 0" begin
        actions = make_mixed(10, 10)
        # Index 1 is NOT a mistake (mistake_flag = 0)
        impacts = compute_error_correction_impact(actions, [1])
        @test impacts[1] == 0.0
    end

    # -----------------------------------------------------------------------
    @testset "analyze_error_growth — insufficient data" begin
        E_x    = [0.1, 0.2]
        x_vals = [2, 3]
        result = analyze_error_growth(E_x, x_vals)
        @test isnan(result["estimated_exponent"])
        @test result["growth_rate"] == "insufficient_data"
    end

    @testset "analyze_error_growth — power-law input" begin
        # Construct E_x = x^0.5 exactly → α should be ≈ 0.5
        x_vals = collect(2:50)
        E_x    = Float64.(x_vals) .^ 0.5

        result = analyze_error_growth(E_x, x_vals)
        @test result["estimated_exponent"] ≈ 0.5  atol=0.05
        @test result["r_squared"] > 0.99
        @test result["growth_rate"] == "square_root"
        @test haskey(result, "erh_satisfied")
        @test haskey(result, "erh_max_ratio")
        @test haskey(result, "erh_violation_rate")
    end

    @testset "analyze_error_growth — superlinear input flagged" begin
        x_vals = collect(2:30)
        E_x    = Float64.(x_vals) .^ 2.0     # superlinear

        result = analyze_error_growth(E_x, x_vals)
        @test result["growth_rate"] == "superlinear"
    end

    # -----------------------------------------------------------------------
    @testset "compute_prime_density — output shapes" begin
        primes = make_mistakes(30)
        centers, densities = compute_prime_density(primes; X_max = 30, bin_size = 5)
        @test length(centers) == length(densities)
        @test sum(densities) <= 30
    end

    @testset "compute_prime_density — prime outside X_max excluded" begin
        primes = [Action(200, 1.0, 0.8, 0.5, 0.3, 1, nothing)]
        centers, densities = compute_prime_density(primes; X_max = 50)
        @test sum(densities) == 0
    end

end  # @testset "EthicalPrimes"
