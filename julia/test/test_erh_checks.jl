using Test

include(joinpath(@__DIR__, "../src/ERHChecks.jl"))
using .ERHChecks

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

"""Construct E_x = C * x^exponent for x = 1..n."""
function power_law_E(n::Int, C::Float64 = 1.0, exponent::Float64 = 0.5)
    x = Float64.(1:n)
    return C .* (x .^ exponent), x
end


@testset "ERHChecks" begin

    # -----------------------------------------------------------------------
    @testset "ERHCheckResult — can be constructed" begin
        r = ERHCheckResult(
            true,   # erh_satisfied
            0.02,   # violation_rate
            10.0,   # bound_value
            0.8,    # max_ratio
            100,    # num_points
            0.95,   # confidence_level
            100,    # sample_size
            "erh_slack_1.5",  # bound_type
            1.0,    # C
            0.1,    # epsilon
            1.5,    # slack_factor
            "TestJudge",  # judge_name
        )
        @test r.erh_satisfied  == true
        @test r.violation_rate ≈ 0.02
        @test r.judge_name     == "TestJudge"
        @test r.bound_type     == "erh_slack_1.5"
        @test r.confidence_level ≈ 0.95
    end

    # -----------------------------------------------------------------------
    @testset "check_erh_bound — ERH satisfied on exact √x data" begin
        E_x, x = power_law_E(100, 0.5, 0.5)   # |E(x)| = 0.5√x ≤ 1·x^0.6
        result  = check_erh_bound(E_x, x)
        @test result["erh_satisfied"] == true
        @test result["num_points"]    == 100
        @test result["max_ratio"]     > 0
        @test result["violation_rate"] <= 0.05
    end

    @testset "check_erh_bound — ERH violated on superlinear data" begin
        # E_x = x^2 >> C·x^0.6  → large violation
        E_x, x = power_law_E(100, 1.0, 2.0)
        result  = check_erh_bound(E_x, x)
        @test result["erh_satisfied"] == false
        @test result["max_ratio"]     > 1.5
    end

    @testset "check_erh_bound — all zeros in E_x" begin
        E_x = zeros(Float64, 50)
        x   = Float64.(1:50)
        result = check_erh_bound(E_x, x)
        # All ratios = 0 → must satisfy
        @test result["erh_satisfied"] == true
        @test result["violation_rate"] == 0.0
    end

    @testset "check_erh_bound — empty valid points" begin
        # x_values all 0 → no valid points
        E_x = [1.0, 2.0]
        x   = [0.0, 0.0]
        result = check_erh_bound(E_x, x)
        @test result["erh_satisfied"] == false
        @test result["num_points"]    == 0
        @test isnan(result["max_ratio"])
    end

    @testset "check_erh_bound — parameter validation: C <= 0" begin
        E_x = [1.0]; x = [1.0]
        @test_throws ArgumentError check_erh_bound(E_x, x; C = 0.0)
        @test_throws ArgumentError check_erh_bound(E_x, x; C = -1.0)
    end

    @testset "check_erh_bound — parameter validation: epsilon < 0" begin
        E_x = [1.0]; x = [1.0]
        @test_throws ArgumentError check_erh_bound(E_x, x; epsilon = -0.1)
    end

    @testset "check_erh_bound — parameter validation: violation_rate out of range" begin
        E_x = [1.0]; x = [1.0]
        @test_throws ArgumentError check_erh_bound(E_x, x; allowed_violation_rate = -0.1)
        @test_throws ArgumentError check_erh_bound(E_x, x; allowed_violation_rate = 1.5)
    end

    @testset "check_erh_bound — parameter validation: slack_factor <= 0" begin
        E_x = [1.0]; x = [1.0]
        @test_throws ArgumentError check_erh_bound(E_x, x; slack_factor = 0.0)
    end

    @testset "check_erh_bound — length mismatch throws" begin
        E_x = [1.0, 2.0]; x = [1.0]
        @test_throws ArgumentError check_erh_bound(E_x, x)
    end

    @testset "check_erh_bound — Integer x_values accepted" begin
        E_x = zeros(Float64, 20)
        x   = collect(1:20)
        result = check_erh_bound(E_x, x)
        @test result["erh_satisfied"] == true
    end

    @testset "check_erh_bound — slack_factor controls decision" begin
        # E_x = 1.2 * x^0.6 → max_ratio = 1.2 > 1 but ≤ 1.5
        E_x, x = power_law_E(100, 1.2, 0.6)
        # With default slack 1.5 and C=1, epsilon=0.1 → bound = x^0.6
        # max_ratio = 1.2 < 1.5 → satisfied
        result_lax = check_erh_bound(E_x, x; slack_factor = 1.5)
        # With strict slack 1.0 → 1.2 > 1.0 → not satisfied
        result_strict = check_erh_bound(E_x, x; slack_factor = 1.0)
        @test result_lax["erh_satisfied"]    == true
        @test result_strict["erh_satisfied"] == false
    end

    @testset "check_erh_bound — Inf/NaN in E_x are ignored" begin
        E_x = [1.0, NaN, Inf, 0.5]
        x   = [1.0, 2.0, 3.0, 4.0]
        result = check_erh_bound(E_x, x)
        # Only 2 valid points (x>0, finite E and x)
        @test result["num_points"] == 2
    end

    # -----------------------------------------------------------------------
    @testset "check_erh_bound_structured — returns ERHCheckResult" begin
        E_x, x = power_law_E(50, 0.5, 0.5)
        r = check_erh_bound_structured(E_x, x)
        @test r isa ERHCheckResult
        @test r.num_points    == 50
        @test r.sample_size   == r.num_points
        @test r.confidence_level ≈ 0.95
        @test r.C        ≈ 1.0
        @test r.epsilon  ≈ 0.1
        @test r.bound_type == "erh_slack_1.5"
    end

    @testset "check_erh_bound_structured — bound_value is finite and positive" begin
        E_x, x = power_law_E(40, 0.3, 0.5)
        r = check_erh_bound_structured(E_x, x)
        @test isfinite(r.bound_value)
        @test r.bound_value > 0
    end

    @testset "check_erh_bound_structured — judge_name stored" begin
        E_x, x = power_law_E(20, 0.5, 0.5)
        r = check_erh_bound_structured(E_x, x; judge_name = "MyJudge")
        @test r.judge_name == "MyJudge"
    end

    @testset "check_erh_bound_structured — nothing judge_name" begin
        E_x, x = power_law_E(20, 0.5, 0.5)
        r = check_erh_bound_structured(E_x, x)
        @test isnothing(r.judge_name)
    end

    @testset "check_erh_bound_structured — strict slack gives erh_strict bound_type" begin
        E_x, x = power_law_E(20, 0.5, 0.5)
        r = check_erh_bound_structured(E_x, x; slack_factor = 1.0)
        @test r.bound_type == "erh_strict"
    end

    @testset "check_erh_bound_structured — matches check_erh_bound verdict" begin
        E_x, x = power_law_E(80, 2.0, 1.5)  # violating
        raw = check_erh_bound(E_x, x)
        str = check_erh_bound_structured(E_x, x)
        @test str.erh_satisfied   == raw["erh_satisfied"]
        @test str.max_ratio       ≈ raw["max_ratio"]
        @test str.violation_rate  ≈ raw["violation_rate"]
    end

    # -----------------------------------------------------------------------
    @testset "check_erh_bound — quantitative: known violation fraction" begin
        # Construct E_x so that exactly 10 out of 100 points violate the bound.
        # bound = C * x^(0.5+epsilon), C=1, epsilon=0.1 → bound = x^0.6
        # |E(x)| > x^0.6 only for the first 10 x-values.
        n   = 100
        x   = Float64.(1:n)
        E_x = zeros(Float64, n)
        # For x in 1..10: set |E| = 2 * x^0.6 (violating)
        for i in 1:10
            E_x[i] = 2.0 * i^0.6
        end
        # For x in 11..100: set |E| = 0.5 * x^0.6 (not violating)
        for i in 11:100
            E_x[i] = 0.5 * i^0.6
        end
        result = check_erh_bound(E_x, x)
        @test result["violation_rate"] ≈ 10/100  atol=0.01
        # max_ratio is governed by the violating portion → > 1
        @test result["max_ratio"] > 1.0
    end

end  # @testset "ERHChecks"
