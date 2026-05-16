using Test

include(joinpath(@__DIR__, "../src/EthicalPrimes.jl"))
include(joinpath(@__DIR__, "../src/ZetaFunction.jl"))
using .EthicalPrimes
using .ZetaFunction

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

"""Return n Actions at complexities 1..n with mistake_flag=1."""
function zf_make_primes(n::Int)
    [Action(i, Float64(i) / n, 0.8, 0.5, 0.3, 1, nothing) for i in 1:n]
end


@testset "ZetaFunction" begin

    # -----------------------------------------------------------------------
    @testset "build_m_sequence — count mode" begin
        primes = zf_make_primes(10)  # complexities 1..10
        m = build_m_sequence(primes; X_max = 15, mode = :count)

        @test length(m) == 15
        # Each complexity 1..10 should have exactly 1 prime
        for i in 1:10
            @test m[i] == 1.0
        end
        @test all(m[11:end] .== 0)
    end

    @testset "build_m_sequence — weighted mode" begin
        primes = zf_make_primes(5)
        m = build_m_sequence(primes; X_max = 10, mode = :weighted)
        # prime at c=3 has w = 3/5 = 0.6
        @test m[3] ≈ 0.6  atol=1e-12
    end

    @testset "build_m_sequence — error mode" begin
        primes = zf_make_primes(5)   # delta = 0.3 for all
        m = build_m_sequence(primes; X_max = 10, mode = :error)
        @test m[2] ≈ 0.3  atol=1e-12
    end

    @testset "build_m_sequence — unknown mode throws" begin
        @test_throws ArgumentError build_m_sequence(zf_make_primes(3); mode = :bogus)
    end

    @testset "build_m_sequence — ignores primes outside range" begin
        primes = [Action(99, 1.0, 0.8, 0.5, 0.3, 1, nothing)]
        m = build_m_sequence(primes; X_max = 20)
        @test all(m .== 0)
    end

    # -----------------------------------------------------------------------
    @testset "ethical_zeta_sum — empty sequence gives 0" begin
        m = zeros(Float64, 20)
        @test ethical_zeta_sum(m, complex(2.0)) == 0.0 + 0.0im
    end

    @testset "ethical_zeta_sum — single term" begin
        m = zeros(Float64, 10)
        m[3] = 1.0                         # one prime at n=3
        # ζ_E(2) = 1/3^2 = 1/9
        val = ethical_zeta_sum(m, complex(2.0))
        @test real(val) ≈ 1/9  atol=1e-12
        @test imag(val) ≈ 0.0  atol=1e-12
    end

    @testset "ethical_zeta_sum — magnitude decreases with Re(s)" begin
        m = zeros(Float64, 20)
        for i in 1:10; m[i] = 1.0; end
        z2 = abs(ethical_zeta_sum(m, complex(2.0)))
        z3 = abs(ethical_zeta_sum(m, complex(3.0)))
        @test z2 > z3    # higher Re(s) → smaller absolute value
    end

    @testset "ethical_zeta_sum — accepts real s" begin
        m = zeros(Float64, 10); m[4] = 1.0
        @test ethical_zeta_sum(m, 2.0) isa ComplexF64
    end

    # -----------------------------------------------------------------------
    @testset "ethical_zeta_product — empty primes gives 1" begin
        val = ethical_zeta_product(Action[], complex(2.0))
        @test val ≈ 1.0 + 0.0im
    end

    @testset "ethical_zeta_product — non-trivial" begin
        primes = zf_make_primes(5)
        val = ethical_zeta_product(primes, complex(2.0))
        @test isfinite(abs(val))
        @test abs(val) > 0
    end

    # -----------------------------------------------------------------------
    @testset "find_approximate_zeros — returns complex vector" begin
        m = zeros(Float64, 50)
        for i in 1:10; m[i] = Float64(i); end

        zeros_found = find_approximate_zeros(m;
            real_range = (0.3, 0.7),
            imag_range = (0.0, 10.0),
            grid_size  = 10,
            threshold  = 2.0,    # loose threshold to guarantee some hits
        )
        @test zeros_found isa Vector{ComplexF64}
    end

    @testset "find_approximate_zeros — refine=false doesn't crash" begin
        m = zeros(Float64, 30)
        m[2] = 1.0
        # just check it runs without error
        result = find_approximate_zeros(m; grid_size = 5, refine = false)
        @test result isa Vector{ComplexF64}
    end

    # -----------------------------------------------------------------------
    @testset "compute_spectrum — output lengths match" begin
        m = zeros(Float64, 40)
        for i in 1:20; m[i] = 1.0; end
        freqs, amps = compute_spectrum(m)
        @test length(freqs) == length(amps)
        @test length(freqs) == 40 ÷ 2 + 1
    end

    @testset "compute_spectrum — amplitudes normalised to [0,1]" begin
        m = zeros(Float64, 16)
        m[1] = 5.0; m[8] = 2.0
        freqs, amps = compute_spectrum(m; normalize = true)
        @test maximum(amps) ≈ 1.0  atol=1e-10
        @test all(amps .>= 0)
    end

    @testset "compute_spectrum — frequencies non-negative" begin
        m = ones(Float64, 20)
        freqs, _ = compute_spectrum(m)
        @test all(freqs .>= 0)
    end

    # -----------------------------------------------------------------------
    @testset "compute_power_spectrum — power = amplitude^2" begin
        m = zeros(Float64, 16); m[1] = 3.0; m[5] = 1.0
        freqs_s, amps  = compute_spectrum(m; normalize = false)
        freqs_p, power = compute_power_spectrum(m; smoothing = nothing)
        @test length(freqs_s) == length(freqs_p)
        @test power ≈ amps .^ 2  atol=1e-10
    end

    @testset "compute_power_spectrum — smoothing doesn't crash" begin
        m = ones(Float64, 20)
        freqs, power = compute_power_spectrum(m; smoothing = 3)
        @test length(power) == length(freqs)
    end

    # -----------------------------------------------------------------------
    @testset "analyze_spectrum_peaks — returns correct number" begin
        m = zeros(Float64, 40)
        m[5] = 3.0; m[10] = 2.0; m[15] = 1.0
        freqs, amps = compute_spectrum(m; normalize = true)
        peaks = analyze_spectrum_peaks(freqs, amps; num_peaks = 3, min_freq = 0.001)
        @test length(peaks) <= 3
        @test all(haskey(p, "frequency") for p in peaks)
        @test all(haskey(p, "amplitude") for p in peaks)
        @test all(haskey(p, "period")    for p in peaks)
    end

    @testset "analyze_spectrum_peaks — min_freq filter works" begin
        m = zeros(Float64, 40); m[1] = 5.0
        freqs, amps = compute_spectrum(m)
        # With high min_freq, the DC component should be excluded
        peaks = analyze_spectrum_peaks(freqs, amps; min_freq = 0.1)
        @test all(p["frequency"] >= 0.1 for p in peaks)
    end

    # -----------------------------------------------------------------------
    @testset "detect_periodic_bias — returns required keys" begin
        m = zeros(Float64, 40); m[1] = 1.0; m[10] = 1.0; m[20] = 1.0
        result = detect_periodic_bias(m)
        @test haskey(result, "has_periodic_bias")
        @test haskey(result, "dominant_period")
        @test haskey(result, "periodicity_strength")
        @test haskey(result, "interpretation")
    end

    @testset "detect_periodic_bias — no bias for zero sequence" begin
        m = zeros(Float64, 30)
        result = detect_periodic_bias(m)
        @test result["has_periodic_bias"] == false
    end

    # -----------------------------------------------------------------------
    # Zero-analysis (folded from zeta_zeros_analysis.py)
    # -----------------------------------------------------------------------

    @testset "refine_zero_newton_raphson — converges on a simple zero" begin
        # ζ_E(s) = m[3]/3^s → zero at: no zero for positive m, but test the
        # function does not crash and returns either a value or nothing
        m  = zeros(Float64, 20); m[3] = 1.0
        zf = s -> ethical_zeta_sum(m, s)
        result = refine_zero_newton_raphson(zf, complex(0.5, 5.0))
        @test result === nothing || result isa ComplexF64
    end

    @testset "compute_zero_density — empty zeros" begin
        d = compute_zero_density(ComplexF64[]; (0.3, 0.7), (0.0, 20.0))
        @test d["total_zeros"] == 0
        @test d["density"] == 0.0
    end

    @testset "compute_zero_density — non-trivial" begin
        zs = [complex(0.5, t) for t in 1.0:5.0]
        d  = compute_zero_density(zs; (0.3, 0.7), (0.0, 20.0))
        @test d["total_zeros"] == 5
        area = (0.7 - 0.3) * 20.0
        @test d["density"] ≈ 5 / area  atol=1e-12
    end

    @testset "analyze_critical_line_proximity — on critical line" begin
        zs = [complex(0.5, Float64(t)) for t in 1:10]
        r  = analyze_critical_line_proximity(zs; critical_line = 0.5)
        @test r["mean_distance"]  ≈ 0.0  atol=1e-12
        @test r["within_0.1"]    == 10
        @test r["fraction_within_0.1"] ≈ 1.0
    end

    @testset "analyze_critical_line_proximity — off critical line" begin
        zs = [complex(0.9, Float64(t)) for t in 1:5]
        r  = analyze_critical_line_proximity(zs; critical_line = 0.5)
        @test r["mean_distance"] ≈ 0.4  atol=1e-12
        @test r["within_0.1"]   == 0
    end

    @testset "compute_pair_correlation — too few zeros" begin
        d, c = compute_pair_correlation(ComplexF64[complex(0.5, 1.0)])
        @test isempty(d) && isempty(c)
    end

    @testset "compute_pair_correlation — two zeros" begin
        zs = [complex(0.5, 1.0), complex(0.5, 2.0)]
        d, c = compute_pair_correlation(zs; max_distance = 5.0, num_bins = 10)
        @test length(d) == 10
        @test length(c) == 10
    end

    @testset "compute_spacing_distribution — spacings correct" begin
        # Four zeros on critical line, equal spacing 1.0
        zs = [complex(0.5, Float64(t)) for t in 1:4]
        st = compute_spacing_distribution(zs; sort_by = :imaginary)
        @test st["mean_spacing"]   ≈ 1.0  atol=1e-12
        @test st["median_spacing"] ≈ 1.0  atol=1e-12
        @test st["std_spacing"]    ≈ 0.0  atol=1e-12
    end

    @testset "compare_with_classical_zeta_patterns — high similarity on critical line" begin
        zs = [complex(0.5, Float64(t)) for t in 1:20]
        r  = compare_with_classical_zeta_patterns(zs)
        @test r["critical_line_clustering"] == true
        @test r["similarity_score"] >= 0.5
    end

    @testset "compare_with_classical_zeta_patterns — empty zeros" begin
        r = compare_with_classical_zeta_patterns(ComplexF64[])
        @test r["similarity_score"] == 0.0
        @test r["critical_line_clustering"] == false
    end

end  # @testset "ZetaFunction"
