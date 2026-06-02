"""
    ZetaFunction

Julia implementation of the ethical zeta function module.

Mirrors erh_core/analysis/zeta_function.py and folds in the advanced
zero-analysis utilities from erh_core/analysis/zeta_zeros_analysis.py.

The "ethical zeta function" is a generating function — inspired by the
Riemann zeta function — that encodes the distribution of ethical primes.
Two representations are supported:

  * Dirichlet series (sum form)     : ζ_E(s) = ∑ₙ m(n)/nˢ
  * Euler product form              : ζ_E(s) = ∏_{p∈P} 1/(1 - c(p)^{-s})

The module also exposes FFT-based spectrum analysis to detect periodic
patterns in judgment errors.
"""
module ZetaFunction

using Statistics: mean, median, std

export build_m_sequence
export ethical_zeta_sum
export ethical_zeta_product
export find_approximate_zeros
export compute_spectrum
export compute_power_spectrum
export analyze_spectrum_peaks
export compute_zeta_grid
export detect_periodic_bias

# Zero-analysis exports (folded from zeta_zeros_analysis.py)
export refine_zero_newton_raphson
export compute_zero_density
export analyze_critical_line_proximity
export compute_pair_correlation
export compute_spacing_distribution
export compare_with_classical_zeta_patterns


# ---------------------------------------------------------------------------
# build_m_sequence
# ---------------------------------------------------------------------------

"""
    build_m_sequence(primes; X_max=200, mode=:count) -> Vector{Float64}

Build the sequence m(n) representing ethical prime distribution.

  m(n) = number of ethical primes at complexity level n

Parameters
----------
- `mode` : `:count`, `:weighted`, or `:error`
"""
function build_m_sequence(
    primes :: Vector,     # Vector{Action} — kept as Vector to avoid circular dep
    ;
    X_max  :: Int    = 200,
    mode   :: Symbol = :count,
) :: Vector{Float64}

    m = zeros(Float64, X_max)

    for prime in primes
        c = prime.c
        (0 < c < X_max) || continue

        if mode == :count
            m[c] += 1.0
        elseif mode == :weighted
            m[c] += prime.w
        elseif mode == :error
            m[c] += isnothing(prime.delta) ? 0.0 : abs(prime.delta)
        else
            throw(ArgumentError("Unknown mode: $mode.  Use :count, :weighted, or :error."))
        end
    end

    return m
end


# ---------------------------------------------------------------------------
# ethical_zeta_sum  (Dirichlet series)
# ---------------------------------------------------------------------------

"""
    ethical_zeta_sum(m, s) -> ComplexF64

Compute the ethical zeta function via Dirichlet series (sum form).

    ζ_E(s) = ∑_{n=1}^{N} m(n) / nˢ

Convergence is best for Re(s) > 1; the function is still evaluated for
other values but may diverge.
"""
function ethical_zeta_sum(
    m :: Vector{Float64},
    s :: Complex{Float64},
) :: ComplexF64

    result = zero(ComplexF64)
    N = length(m)

    for n in 1:(N - 1)
        m[n] == 0 && continue
        try
            result += m[n] / (complex(Float64(n)) ^ s)
        catch
            # skip numerically problematic terms
        end
    end

    return result
end

# Accept real s as well
ethical_zeta_sum(m::Vector{Float64}, s::Real) =
    ethical_zeta_sum(m, complex(Float64(s)))


# ---------------------------------------------------------------------------
# ethical_zeta_product  (Euler product)
# ---------------------------------------------------------------------------

"""
    ethical_zeta_product(primes, s; max_terms=100) -> ComplexF64

Compute the ethical zeta function via Euler product formula.

    ζ_E(s) = ∏_{p ∈ P} 1 / (1 − c(p)^{−s})

This is a toy model inspired by the classical Euler product for ζ(s).
Convergence requires Re(s) > 1 in general.
"""
function ethical_zeta_product(
    primes    :: Vector,
    s         :: Complex{Float64};
    max_terms :: Int = 100,
) :: ComplexF64

    isempty(primes) && return one(ComplexF64)

    subset  = primes[1:min(max_terms, length(primes))]
    product = one(ComplexF64)

    for prime in subset
        c = prime.c
        c <= 0 && continue
        try
            term = one(ComplexF64) / (one(ComplexF64) - complex(Float64(c)) ^ (-s))
            product *= term
        catch
            # skip overflow/zero-division terms
        end
    end

    return product
end

ethical_zeta_product(primes::Vector, s::Real; kw...) =
    ethical_zeta_product(primes, complex(Float64(s)); kw...)


# ---------------------------------------------------------------------------
# find_approximate_zeros
# ---------------------------------------------------------------------------

"""
    find_approximate_zeros(m; real_range=(0.3,0.7), imag_range=(0.0,50.0),
                           grid_size=50, threshold=0.1, refine=false)
          -> Vector{ComplexF64}

Find approximate zeros of ζ_E(s) by grid search.

If `refine=true`, each candidate is refined with Newton-Raphson via
`refine_zero_newton_raphson`.
"""
function find_approximate_zeros(
    m           :: Vector{Float64};
    real_range  :: Tuple{Float64,Float64} = (0.3, 0.7),
    imag_range  :: Tuple{Float64,Float64} = (0.0, 50.0),
    grid_size   :: Int                    = 50,
    threshold   :: Float64                = 0.1,
    refine      :: Bool                   = false,
) :: Vector{ComplexF64}

    real_vals = range(real_range[1], real_range[2]; length = grid_size)
    imag_vals = range(imag_range[1], imag_range[2]; length = grid_size)

    zeros_found = ComplexF64[]

    for re in real_vals, im in imag_vals
        s = complex(re, im)
        try
            zeta_val = ethical_zeta_sum(m, s)
            abs(zeta_val) < threshold && push!(zeros_found, s)
        catch
            continue
        end
    end

    if refine && !isempty(zeros_found)
        zf(s) = ethical_zeta_sum(m, s)
        zeros_found = map(zeros_found) do z0
            refined = refine_zero_newton_raphson(zf, z0)
            isnothing(refined) ? z0 : refined
        end
    end

    return zeros_found
end


# ---------------------------------------------------------------------------
# compute_spectrum
# ---------------------------------------------------------------------------

"""
    compute_spectrum(m; normalize=true) -> (frequencies, amplitudes)

Compute the Fourier spectrum of the ethical prime distribution via FFT.

Returns only the non-negative frequency components.  If `normalize=true`,
amplitudes are scaled to [0, 1].

Analogous to studying the "spectrum of primes" in number theory.
"""
function compute_spectrum(
    m         :: Vector{Float64};
    normalize :: Bool = true,
) :: Tuple{Vector{Float64}, Vector{Float64}}

    N        = length(m)
    spectrum = fft_magnitude(m)               # magnitudes of full FFT

    freqs      = fftfreq_positive(N)
    n_pos      = length(freqs)
    amplitudes = spectrum[1:n_pos]

    if normalize && maximum(amplitudes) > 0
        amplitudes = amplitudes ./ maximum(amplitudes)
    end

    return freqs, amplitudes
end


# ---------------------------------------------------------------------------
# compute_power_spectrum
# ---------------------------------------------------------------------------

"""
    compute_power_spectrum(m; smoothing=nothing) -> (frequencies, power)

Compute the power spectrum (squared magnitudes).

Optionally apply a moving-average smoothing of window `smoothing`.
"""
function compute_power_spectrum(
    m         :: Vector{Float64};
    smoothing :: Union{Int, Nothing} = nothing,
) :: Tuple{Vector{Float64}, Vector{Float64}}

    freqs, amps = compute_spectrum(m; normalize = false)
    power = amps .^ 2

    if !isnothing(smoothing) && smoothing > 1
        power = _moving_average(power, smoothing)
    end

    return freqs, power
end


# ---------------------------------------------------------------------------
# analyze_spectrum_peaks
# ---------------------------------------------------------------------------

"""
    analyze_spectrum_peaks(frequencies, amplitudes; num_peaks=5, min_freq=0.01)
          -> Vector{Dict}

Identify the dominant peaks in the spectrum.

Each returned dict contains `"frequency"`, `"amplitude"`, and `"period"`.
"""
function analyze_spectrum_peaks(
    frequencies :: Vector{Float64},
    amplitudes  :: Vector{Float64};
    num_peaks   :: Int     = 5,
    min_freq    :: Float64 = 0.01,
) :: Vector{Dict{String, Any}}

    mask       = frequencies .>= min_freq
    freq_f     = frequencies[mask]
    amp_f      = amplitudes[mask]

    isempty(amp_f) && return Dict{String,Any}[]

    sorted_idx = sortperm(amp_f; rev = true)
    k          = min(num_peaks, length(sorted_idx))

    return [
        Dict{String,Any}(
            "frequency" => freq_f[sorted_idx[i]],
            "amplitude" => amp_f[sorted_idx[i]],
            "period"    => freq_f[sorted_idx[i]] > 0 ? 1.0 / freq_f[sorted_idx[i]] : Inf,
        )
        for i in 1:k
    ]
end


# ---------------------------------------------------------------------------
# compute_zeta_grid
# ---------------------------------------------------------------------------

"""
    compute_zeta_grid(m; real_range=(0.1,1.5), imag_range=(0.0,30.0),
                      grid_size=100)
          -> (real_grid, imag_grid, magnitude_grid)

Evaluate |ζ_E(s)| on a 2-D grid in the complex plane for visualisation.
"""
function compute_zeta_grid(
    m          :: Vector{Float64};
    real_range :: Tuple{Float64,Float64} = (0.1, 1.5),
    imag_range :: Tuple{Float64,Float64} = (0.0, 30.0),
    grid_size  :: Int                    = 100,
) :: Tuple{Matrix{Float64}, Matrix{Float64}, Matrix{Float64}}

    real_vals = collect(range(real_range[1], real_range[2]; length = grid_size))
    imag_vals = collect(range(imag_range[1], imag_range[2]; length = grid_size))

    real_grid = [real_vals[j] for i in 1:grid_size, j in 1:grid_size]
    imag_grid = [imag_vals[i] for i in 1:grid_size, j in 1:grid_size]
    mag_grid  = fill(NaN, grid_size, grid_size)

    for i in 1:grid_size, j in 1:grid_size
        s = complex(real_grid[i,j], imag_grid[i,j])
        try
            mag_grid[i,j] = abs(ethical_zeta_sum(m, s))
        catch
            mag_grid[i,j] = NaN
        end
    end

    return real_grid, imag_grid, mag_grid
end


# ---------------------------------------------------------------------------
# detect_periodic_bias
# ---------------------------------------------------------------------------

"""
    detect_periodic_bias(m; significance_threshold=0.3) -> Dict

Detect if there is a significant periodic structure in misjudgments.
"""
function detect_periodic_bias(
    m                       :: Vector{Float64};
    significance_threshold  :: Float64 = 0.3,
) :: Dict{String, Any}

    freqs, amps = compute_spectrum(m; normalize = true)
    peaks = analyze_spectrum_peaks(freqs, amps; num_peaks = 5)

    has_bias = !isempty(peaks) && peaks[1]["amplitude"] > significance_threshold

    dominant_period = isempty(peaks) ? nothing : peaks[1]["period"]
    top_periods     = [p["period"]    for p in peaks]
    top_amps        = [p["amplitude"] for p in peaks]

    interp = if has_bias
        "Strong periodic pattern detected: errors cluster every ~$(round(dominant_period; digits=1)) " *
        "complexity units. This suggests structural bias in the judgment system."
    else
        "No strong periodic pattern detected. Errors appear relatively " *
        "uniformly distributed across complexity levels."
    end

    return Dict{String,Any}(
        "has_periodic_bias"     => has_bias,
        "dominant_period"       => dominant_period,
        "periodicity_strength"  => isempty(peaks) ? 0.0 : peaks[1]["amplitude"],
        "top_periods"           => top_periods,
        "top_amplitudes"        => top_amps,
        "interpretation"        => interp,
    )
end


# ===========================================================================
# Zero-analysis utilities (folded from zeta_zeros_analysis.py)
# ===========================================================================

"""
    refine_zero_newton_raphson(zeta_func, s0; max_iter=20, tol=1e-6)
          -> Union{ComplexF64, Nothing}

Refine a zero location using Newton-Raphson iteration.

Numerical derivative is computed with a central difference of step h = 1e-8.
Returns `nothing` if the iteration does not converge.
"""
function refine_zero_newton_raphson(
    zeta_func :: Function,
    s0        :: Complex{Float64};
    max_iter  :: Int     = 20,
    tol       :: Float64 = 1e-6,
) :: Union{ComplexF64, Nothing}

    s = s0
    h = complex(1e-8)

    for _ in 1:max_iter
        zv = try zeta_func(s) catch; return nothing end

        abs(zv) < tol && return s

        dz = try (zeta_func(s + h) - zeta_func(s - h)) / (2 * h) catch; return nothing end

        abs(dz) < 1e-10 && break

        s_new = s - zv / dz

        abs(s_new - s) < tol && return s_new

        s = s_new
    end

    return nothing
end

refine_zero_newton_raphson(f::Function, s0::Complex; kw...) =
    refine_zero_newton_raphson(f, ComplexF64(s0); kw...)


"""
    compute_zero_density(zeros, real_range, imag_range) -> Dict

Compute zero density statistics over a rectangular region.
"""
function compute_zero_density(
    zeros      :: Vector{<:Complex},
    real_range :: Tuple{Float64,Float64},
    imag_range :: Tuple{Float64,Float64},
) :: Dict{String, Any}

    isempty(zeros) && return Dict{String,Any}(
        "total_zeros" => 0, "area" => 0.0,
        "density" => 0.0, "zeros_per_unit_area" => 0.0,
    )

    area = (real_range[2] - real_range[1]) * (imag_range[2] - imag_range[1])

    return Dict{String,Any}(
        "total_zeros"        => length(zeros),
        "area"               => area,
        "density"            => area > 0 ? length(zeros) / area : 0.0,
        "zeros_per_unit_area" => area > 0 ? length(zeros) / area : 0.0,
    )
end


"""
    analyze_critical_line_proximity(zeros; critical_line=0.5) -> Dict

Analyse how close the zeros are to the critical line Re(s) = `critical_line`.
"""
function analyze_critical_line_proximity(
    zeros         :: Vector{<:Complex};
    critical_line :: Float64 = 0.5,
) :: Dict{String, Any}

    if isempty(zeros)
        return Dict{String,Any}(
            "mean_distance"   => NaN, "median_distance" => NaN,
            "min_distance"    => NaN, "max_distance"    => NaN,
            "within_0.1"      => 0,   "within_0.05"     => 0,
            "within_0.01"     => 0,
        )
    end

    dists = [abs(real(z) - critical_line) for z in zeros]

    return Dict{String,Any}(
        "mean_distance"       => mean(dists),
        "median_distance"     => median(dists),
        "min_distance"        => minimum(dists),
        "max_distance"        => maximum(dists),
        "std_distance"        => std(dists),
        "within_0.1"          => count(d -> d < 0.1,  dists),
        "within_0.05"         => count(d -> d < 0.05, dists),
        "within_0.01"         => count(d -> d < 0.01, dists),
        "fraction_within_0.1" => count(d -> d < 0.1,  dists) / length(zeros),
        "fraction_within_0.05"=> count(d -> d < 0.05, dists) / length(zeros),
        "fraction_within_0.01"=> count(d -> d < 0.01, dists) / length(zeros),
    )
end


"""
    compute_pair_correlation(zeros; max_distance=5.0, num_bins=50)
          -> (distances, correlation)

Compute the pair correlation function for zeros.
"""
function compute_pair_correlation(
    zeros        :: Vector{<:Complex};
    max_distance :: Float64 = 5.0,
    num_bins     :: Int     = 50,
) :: Tuple{Vector{Float64}, Vector{Float64}}

    length(zeros) < 2 && return (Float64[], Float64[])

    pair_dists = Float64[]
    for i in 1:length(zeros), j in (i+1):length(zeros)
        d = abs(zeros[i] - zeros[j])
        d <= max_distance && push!(pair_dists, d)
    end

    isempty(pair_dists) && return (Float64[], Float64[])

    bin_width = max_distance / num_bins
    edges     = range(0.0, max_distance; length = num_bins + 1)
    centers   = Float64[(edges[i] + edges[i+1]) / 2.0 for i in 1:num_bins]
    hist      = zeros(Int, num_bins)

    for d in pair_dists
        b = min(num_bins, floor(Int, d / bin_width) + 1)
        hist[b] += 1
    end

    expected_density = length(pair_dists) / max_distance
    correlation = hist ./ (expected_density * bin_width * length(zeros))

    return centers, correlation
end


"""
    compute_spacing_distribution(zeros; sort_by=:imaginary) -> Dict

Compute spacing distribution between consecutive zeros.
"""
function compute_spacing_distribution(
    zeros   :: Vector{<:Complex};
    sort_by :: Symbol = :imaginary,
) :: Dict{String, Any}

    length(zeros) < 2 && return Dict{String,Any}(
        "mean_spacing" => NaN, "median_spacing" => NaN,
        "std_spacing"  => NaN, "spacings"       => Float64[],
    )

    sorted_z = if sort_by == :imaginary
        sort(zeros; by = z -> imag(z))
    elseif sort_by == :real
        sort(zeros; by = z -> real(z))
    else  # magnitude
        sort(zeros; by = abs)
    end

    spacings = [abs(sorted_z[i+1] - sorted_z[i]) for i in 1:(length(sorted_z)-1)]

    return Dict{String,Any}(
        "mean_spacing"   => mean(spacings),
        "median_spacing" => median(spacings),
        "std_spacing"    => std(spacings),
        "min_spacing"    => minimum(spacings),
        "max_spacing"    => maximum(spacings),
        "spacings"       => spacings,
    )
end


"""
    compare_with_classical_zeta_patterns(zeros) -> Dict

Compare ethical zeta zero patterns with known classical ζ(s) patterns.
"""
function compare_with_classical_zeta_patterns(
    zeros :: Vector{<:Complex},
) :: Dict{String, Any}

    isempty(zeros) && return Dict{String,Any}(
        "critical_line_clustering" => false,
        "spacing_regularity"       => NaN,
        "similarity_score"         => 0.0,
    )

    cl_analysis = analyze_critical_line_proximity(zeros; critical_line = 0.5)
    clusters    = get(cl_analysis, "fraction_within_0.1", 0.0) > 0.5

    spacing     = compute_spacing_distribution(zeros; sort_by = :imaginary)
    ms          = get(spacing, "mean_spacing",  NaN)
    ss          = get(spacing, "std_spacing",   NaN)
    spacing_cv  = (isnan(ms) || ms == 0) ? NaN : ss / ms
    regular     = isnan(spacing_cv) ? false : spacing_cv < 0.5

    similarity = 0.0
    clusters   && (similarity += 0.5)
    regular    && (similarity += 0.3)
    get(cl_analysis, "fraction_within_0.05", 0.0) > 0.3 && (similarity += 0.2)

    return Dict{String,Any}(
        "critical_line_clustering"  => clusters,
        "spacing_regularity"        => regular,
        "spacing_cv"                => spacing_cv,
        "similarity_score"          => similarity,
        "critical_line_analysis"    => cl_analysis,
    )
end


# ===========================================================================
# Private helpers
# ===========================================================================

"""
Discrete Fourier Transform magnitudes.  Uses a pure-Julia DFT so we avoid
depending on an external FFT package — correctness over speed for this module.
"""
function fft_magnitude(x::Vector{Float64}) :: Vector{Float64}
    N = length(x)
    X = Vector{ComplexF64}(undef, N)
    for k in 0:(N-1)
        s = zero(ComplexF64)
        for n in 0:(N-1)
            s += x[n+1] * exp(-2π * im * k * n / N)
        end
        X[k+1] = s
    end
    return abs.(X)
end

"""
Positive frequencies for an N-point DFT, analogous to `np.fft.fftfreq`.
"""
function fftfreq_positive(N::Int) :: Vector{Float64}
    n_pos = N ÷ 2 + 1
    return [k / N for k in 0:(n_pos-1)]
end

"""
Simple causal moving average of window `w`.
"""
function _moving_average(x::Vector{Float64}, w::Int) :: Vector{Float64}
    n   = length(x)
    out = similar(x)
    for i in 1:n
        lo = max(1, i - w ÷ 2)
        hi = min(n, i + w ÷ 2)
        out[i] = mean(x[lo:hi])
    end
    return out
end

end  # module ZetaFunction
