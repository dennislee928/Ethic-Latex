using Test

include(joinpath(@__DIR__, "../src/EthicalPrimes.jl"))
include(joinpath(@__DIR__, "../src/ERHStatistics.jl"))
using .EthicalPrimes
using .ERHStatistics

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

"""|E(x)| = C * x^alpha for x = 1..n."""
function stat_power_E(n::Int, C::Float64 = 1.0, alpha::Float64 = 0.5)
    x = Float64.(1:n)
    return C .* (x .^ alpha), x
end

"""Actions with known delta values."""
function stat_make_actions(n::Int; delta_fn = i -> Float64(i) * 0.02)
    [Action(i, 1.0, 0.9, 0.9 - delta_fn(i), delta_fn(i), delta_fn(i) > 0.3 ? 1 : 0, nothing)
     for i in 1:n]
end


@testset "ERHStatistics" begin

    # -----------------------------------------------------------------------
    @testset "fit_error_growth — insufficient data" begin
        E_x = [0.1, 0.2]
        x   = [2.0, 3.0]
        r   = fit_error_growth(E_x, x)
        @test haskey(r, "error")
        @test r["error"] == "insufficient_data"
    end

    @testset "fit_error_growth — power_law recovers exponent" begin
        # Exact power-law data: |E| = 1.5 * x^0.7
        E_x, x = stat_power_E(60, 1.5, 0.7)
        r = fit_error_growth(E_x, x; model = :power_law)
        @test !haskey(r, "error")
        @test r["exponent"] ≈ 0.7   atol=0.05
        @test r["constant"] ≈ 1.5   atol=0.1
        @test r["r_squared"] > 0.99
        @test r["num_points"] > 0
    end

    @testset "fit_error_growth — linear model" begin
        x   = Float64.(2:50)
        E_x = 0.5 .* x .+ 1.0
        r   = fit_error_growth(E_x, x; model = :linear)
        @test !haskey(r, "error")
        @test r["slope"]     ≈ 0.5  atol=0.05
        @test r["intercept"] ≈ 1.0  atol=0.1
        @test r["r_squared"] > 0.99
    end

    @testset "fit_error_growth — quadratic model" begin
        x   = Float64.(2:30)
        E_x = 0.01 .* x .^ 2 .+ 0.5 .* x .+ 0.2
        r   = fit_error_growth(E_x, x; model = :quadratic)
        @test !haskey(r, "error")
        @test r["r_squared"] > 0.99
        @test haskey(r, "coefficients")
    end

    @testset "fit_error_growth — logarithmic model" begin
        x   = Float64.(2:40)
        E_x = 3.0 .* log.(x) .+ 0.5
        r   = fit_error_growth(E_x, x; model = :logarithmic)
        @test !haskey(r, "error")
        @test r["coefficient"] ≈ 3.0  atol=0.1
        @test r["constant"]    ≈ 0.5  atol=0.2
    end

    @testset "fit_error_growth — unknown model returns error" begin
        E_x, x = stat_power_E(20)
        r = fit_error_growth(E_x, x; model = :foobar)
        @test haskey(r, "error")
    end

    @testset "fit_error_growth — integer x_values accepted" begin
        E_x, _ = stat_power_E(30)
        r = fit_error_growth(E_x, collect(1:30); model = :power_law)
        @test !haskey(r, "error")
    end

    @testset "fit_power_law_to_data — same result as fit_error_growth" begin
        E_x, x = stat_power_E(40, 2.0, 0.6)
        r1 = fit_error_growth(E_x, x)
        r2 = fit_power_law_to_data(x, E_x)
        @test r1["exponent"] ≈ r2["exponent"]   atol=1e-10
    end

    # -----------------------------------------------------------------------
    @testset "bootstrap_exponent_ci — insufficient data returns NaN" begin
        E_x = [0.1, 0.2, 0.3]
        x   = [1.0, 2.0, 3.0]
        r   = bootstrap_exponent_ci(E_x, x)
        @test isnan(r["alpha_hat"])
        @test isnan(r["alpha_ci_low"])
    end

    @testset "bootstrap_exponent_ci — recovers approximate exponent" begin
        E_x, x = stat_power_E(80, 1.0, 0.5)
        r = bootstrap_exponent_ci(E_x, x; n_bootstrap = 100)
        @test r["alpha_hat"]    ≈ 0.5  atol=0.1
        @test r["alpha_ci_low"]  < r["alpha_hat"]
        @test r["alpha_ci_high"] > r["alpha_hat"]
        @test r["num_samples"]   > 0
    end

    @testset "bootstrap_exponent_ci — CI contains point estimate" begin
        E_x, x = stat_power_E(60, 1.0, 0.7)
        r = bootstrap_exponent_ci(E_x, x; n_bootstrap = 200, ci = 0.95)
        @test r["alpha_ci_low"]  <= r["alpha_hat"]
        @test r["alpha_ci_high"] >= r["alpha_hat"]
    end

    @testset "bootstrap_exponent_ci — integer x_values accepted" begin
        E_x, _ = stat_power_E(40)
        r = bootstrap_exponent_ci(E_x, collect(1:40); n_bootstrap = 50)
        @test !isnan(r["alpha_hat"])
    end

    # -----------------------------------------------------------------------
    @testset "detect_structural_bias — insufficient data" begin
        actions = stat_make_actions(5)
        r = detect_structural_bias(actions)
        @test haskey(r, "error")
    end

    @testset "detect_structural_bias — basic keys present" begin
        actions = stat_make_actions(50)
        r = detect_structural_bias(actions)
        @test haskey(r, "complexity_error_correlation")
        @test haskey(r, "correlation_p_value")
        @test haskey(r, "correlation_significant")
        @test haskey(r, "bins")
        @test haskey(r, "monotonic_increasing")
        @test haskey(r, "interpretation")
    end

    @testset "detect_structural_bias — positive correlation detected" begin
        # delta increases with complexity → positive correlation
        actions = [Action(i, 1.0, 0.9, 0.9 - Float64(i)*0.01,
                          Float64(i)*0.01, 0, nothing) for i in 1:60]
        r = detect_structural_bias(actions)
        @test r["complexity_error_correlation"] > 0
    end

    @testset "detect_structural_bias — bins have correct length" begin
        actions = stat_make_actions(50)
        r = detect_structural_bias(actions; complexity_bins = 5)
        @test length(r["bins"]["centers"])     == 5
        @test length(r["bins"]["mean_errors"]) == 5
        @test length(r["bins"]["counts"])      == 5
    end

    # -----------------------------------------------------------------------
    @testset "calculate_evs — perfect system" begin
        evs = calculate_evs(1.0, 1.0, 0.0)
        @test evs ≈ 1.0  atol=1e-12
    end

    @testset "calculate_evs — zero stability → EVS = 0" begin
        @test calculate_evs(0.0, 1.0, 0.0) == 0.0
    end

    @testset "calculate_evs — zero fairness → EVS = 0" begin
        @test calculate_evs(1.0, 0.0, 0.0) == 0.0
    end

    @testset "calculate_evs — full polarization zeros EVS" begin
        evs = calculate_evs(0.8, 0.8, 1.0)
        @test evs ≈ 0.0  atol=1e-12
    end

    @testset "calculate_evs — polarization clipped to [0,1]" begin
        # Polarization > 1 should be treated as 1
        evs_clipped = calculate_evs(0.8, 0.8, 2.0)
        evs_at_one  = calculate_evs(0.8, 0.8, 1.0)
        @test evs_clipped ≈ evs_at_one  atol=1e-12
    end

    @testset "calculate_evs — formula: harmonic mean × (1 - polar)" begin
        s = 0.6; f = 0.8; p = 0.2
        hm  = 2 * s * f / (s + f)
        expected = hm * (1 - p)
        @test calculate_evs(s, f, p) ≈ expected  atol=1e-12
    end

    # -----------------------------------------------------------------------
    @testset "compute_stability_metric — perfect fit gives high R²" begin
        # E_x = C * x^0.5 exactly → R² ≈ 1 (with fixed target_exponent = 0.5)
        E_x, x = stat_power_E(50, 0.8, 0.5)
        stab = compute_stability_metric(E_x, x; target_exponent = 0.5)
        @test stab > 0.99
    end

    @testset "compute_stability_metric — bad fit gives lower R²" begin
        E_x, x = stat_power_E(50, 1.0, 1.5)  # exponent 1.5, not 0.5
        stab = compute_stability_metric(E_x, x; target_exponent = 0.5)
        @test stab < 0.8
    end

    @testset "compute_stability_metric — output in [0,1]" begin
        E_x, x = stat_power_E(40, 1.0, 0.9)
        stab = compute_stability_metric(E_x, x)
        @test 0.0 <= stab <= 1.0
    end

    @testset "compute_stability_metric — insufficient data returns 0" begin
        @test compute_stability_metric([0.5, 0.6], [2.0, 3.0]) == 0.0
    end

    # -----------------------------------------------------------------------
    @testset "calculate_von_neumann_entropy — pure state (rank-1) = 0" begin
        # ρ = |0><0| → single eigenvalue 1 → entropy = 0
        rho = [1.0 0.0; 0.0 0.0]
        H = calculate_von_neumann_entropy(rho)
        @test H ≈ 0.0  atol=1e-10
    end

    @testset "calculate_von_neumann_entropy — maximally mixed 2x2 = log(2)" begin
        rho = [0.5 0.0; 0.0 0.5]
        H = calculate_von_neumann_entropy(rho)
        @test H ≈ log(2)  atol=1e-8
    end

    @testset "calculate_von_neumann_entropy — 3×3 maximally mixed = log(3)" begin
        rho = (1/3) .* Matrix{Float64}(I, 3, 3)
        H = calculate_von_neumann_entropy(rho)
        @test H ≈ log(3)  atol=1e-8
    end

    @testset "calculate_von_neumann_entropy — non-negative" begin
        rho = [0.7 0.0; 0.0 0.3]
        H = calculate_von_neumann_entropy(rho)
        @test H >= 0
    end

end  # @testset "ERHStatistics"
