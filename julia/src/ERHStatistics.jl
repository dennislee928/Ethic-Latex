"""
    ERHStatistics

Julia implementation of the ERH statistics module.

Mirrors erh_core/analysis/statistics.py and folds in EVS, dual-metrics,
conservative-judge anomaly, and the Von Neumann entropy helper.

Key functions
-------------
- `fit_error_growth`              : fit a model to |E(x)|
- `bootstrap_exponent_ci`         : bootstrap 95 % CI for the growth exponent α
- `detect_structural_bias`        : correlation between complexity and |error|
- `calculate_evs`                 : Ethical Viability Score (EVS)
- `compute_stability_metric`      : goodness of fit to the x^½ ERH boundary
- `calculate_von_neumann_entropy` : Von Neumann entropy of a density matrix
"""
module ERHStatistics

using Statistics: mean, median, std, var, cor
using LinearAlgebra: eigvals, eigvalsh, norm, I
using Random: default_rng

export fit_error_growth
export fit_power_law_to_data
export bootstrap_exponent_ci
export detect_structural_bias
export calculate_evs
export compute_stability_metric
export calculate_von_neumann_entropy

# ---------------------------------------------------------------------------
# fit_error_growth
# ---------------------------------------------------------------------------

"""
    fit_error_growth(E_x, x_values; model=:power_law) -> Dict{String, Any}

Fit a model to the error growth |E(x)|.

Supported models
----------------
- `:power_law`  : |E(x)| = C · x^α   (log–log regression)
- `:linear`     : |E(x)| = a · x + b
- `:quadratic`  : |E(x)| = a · x² + b · x + c
- `:logarithmic`: |E(x)| = a · log(x) + b

Returns a `Dict` with at minimum keys `"model"`, `"r_squared"`, `"rmse"`,
`"num_points"`, and model-specific parameter keys.
On failure, returns `Dict("error" => message)`.
"""
function fit_error_growth(
    E_x      :: Vector{Float64},
    x_values :: Vector{Float64};
    model    :: Symbol = :power_law,
) :: Dict{String, Any}

    abs_E     = abs.(E_x)
    valid     = (abs_E .> 0) .& (x_values .> 1)

    count(valid) < 3 && return Dict{String,Any}("error" => "insufficient_data")

    x = x_values[valid]
    y = abs_E[valid]

    try
        if model == :power_law
            # log|E| = log(C) + α·log(x) — ordinary least squares in log space
            lx     = log.(x)
            ly     = log.(y)
            alpha, log_C = _ols(lx, ly)
            C      = exp(log_C)
            y_pred = C .* (x .^ alpha)

            return _result_dict(:power_law, y, y_pred, x;
                "constant"  => C,
                "exponent"  => alpha,
                "formula"   => "$(round(C;digits=3)) * x^$(round(alpha;digits=3))",
            )

        elseif model == :linear
            a, b   = _ols(x, y)
            y_pred = a .* x .+ b

            return _result_dict(:linear, y, y_pred, x;
                "slope"     => a,
                "intercept" => b,
                "formula"   => "$(round(a;digits=3)) * x + $(round(b;digits=3))",
            )

        elseif model == :quadratic
            coeffs = _polyfit(x, y, 2)          # [c2, c1, c0]
            y_pred = _polyval(coeffs, x)

            return _result_dict(:quadratic, y, y_pred, x;
                "coefficients" => coeffs,
                "formula"      => "$(round(coeffs[1];digits=4)) * x^2 + " *
                                  "$(round(coeffs[2];digits=3)) * x + " *
                                  "$(round(coeffs[3];digits=3))",
            )

        elseif model == :logarithmic
            lx     = log.(x)
            a, b   = _ols(lx, y)
            y_pred = a .* lx .+ b

            return _result_dict(:logarithmic, y, y_pred, x;
                "coefficient" => a,
                "constant"    => b,
                "formula"     => "$(round(a;digits=3)) * log(x) + $(round(b;digits=3))",
            )

        else
            return Dict{String,Any}("error" => "unknown_model: $model")
        end

    catch e
        return Dict{String,Any}("error" => string(e))
    end
end

# Convenience overload
fit_error_growth(E_x::Vector{Float64}, x_values::Vector{Int}; kw...) =
    fit_error_growth(E_x, Float64.(x_values); kw...)


"""
    fit_power_law_to_data(x_values, error_values; model=:power_law) -> Dict

Thin wrapper around `fit_error_growth` with argument order matching the
Python `fit_power_law_to_data` signature.
"""
fit_power_law_to_data(
    x_values     :: Vector{<:Real},
    error_values :: Vector{<:Real};
    model        :: Symbol = :power_law,
) = fit_error_growth(Float64.(error_values), Float64.(x_values); model = model)


# ---------------------------------------------------------------------------
# bootstrap_exponent_ci
# ---------------------------------------------------------------------------

"""
    bootstrap_exponent_ci(E_x, x_values; n_bootstrap=500, ci=0.95)
          -> Dict{String, Float64}

Estimate uncertainty for the growth exponent α via bootstrap.

Resamples the valid (x, |E(x)|) pairs with replacement `n_bootstrap` times
and refits the log–log slope each time to build an empirical distribution.

Returns keys: `"alpha_hat"`, `"alpha_ci_low"`, `"alpha_ci_high"`,
`"num_samples"`.
"""
function bootstrap_exponent_ci(
    E_x       :: Vector{Float64},
    x_values  :: Vector{<:Real};
    n_bootstrap :: Int     = 500,
    ci          :: Float64 = 0.95,
) :: Dict{String, Float64}

    abs_E = abs.(E_x)
    xf    = Float64.(x_values)
    valid = (abs_E .> 0) .& (xf .> 1)

    n_valid = count(valid)

    if n_valid < 5
        return Dict{String,Float64}(
            "alpha_hat"      => NaN,
            "alpha_ci_low"   => NaN,
            "alpha_ci_high"  => NaN,
            "num_samples"    => Float64(n_valid),
        )
    end

    x    = xf[valid]
    y    = abs_E[valid]
    lx   = log.(x)
    ly   = log.(y)

    alpha_hat, _ = _ols(lx, ly)

    rng    = default_rng()
    n      = length(lx)
    alphas = Float64[]

    for _ in 1:n_bootstrap
        idx = rand(rng, 1:n, n)
        bx  = lx[idx]
        by  = ly[idx]
        std(bx) == 0 || std(by) == 0 && continue
        a, _ = _ols(bx, by)
        push!(alphas, a)
    end

    if isempty(alphas)
        return Dict{String,Float64}(
            "alpha_hat"      => alpha_hat,
            "alpha_ci_low"   => NaN,
            "alpha_ci_high"  => NaN,
            "num_samples"    => Float64(n),
        )
    end

    q_lo = (1 - ci) / 2
    q_hi = 1 - q_lo
    lower = _quantile(alphas, q_lo)
    upper = _quantile(alphas, q_hi)

    return Dict{String,Float64}(
        "alpha_hat"      => alpha_hat,
        "alpha_ci_low"   => lower,
        "alpha_ci_high"  => upper,
        "num_samples"    => Float64(n),
    )
end


# ---------------------------------------------------------------------------
# detect_structural_bias
# ---------------------------------------------------------------------------

"""
    detect_structural_bias(actions; complexity_bins=10) -> Dict{String, Any}

Detect structural bias correlated with complexity.

Uses Pearson correlation between complexity c and |error|, and bins the
data to reveal monotonic trends.
"""
function detect_structural_bias(
    actions         :: Vector;
    complexity_bins :: Int = 10,
) :: Dict{String, Any}

    valid_actions = [a for a in actions if !isnothing(a.delta)]
    length(valid_actions) < 10 && return Dict{String,Any}("error" => "insufficient_data")

    complexities = Float64[a.c       for a in valid_actions]
    abs_errors   = Float64[abs(a.delta) for a in valid_actions]

    corr, p_value = _pearsonr(complexities, abs_errors)

    c_min = minimum(complexities)
    c_max = maximum(complexities)
    bins  = range(c_min, c_max; length = complexity_bins + 1)

    centers        = Float64[]
    bin_mean_err   = Float64[]
    bin_std_err    = Float64[]
    bin_counts     = Int[]

    for i in 1:complexity_bins
        lo = bins[i];  hi = bins[i+1]
        mask = if i == complexity_bins
            (complexities .>= lo) .& (complexities .<= hi)
        else
            (complexities .>= lo) .& (complexities .< hi)
        end

        push!(centers, (lo + hi) / 2)
        be = abs_errors[mask]
        if !isempty(be)
            push!(bin_mean_err, mean(be))
            push!(bin_std_err,  std(be))
            push!(bin_counts,   length(be))
        else
            push!(bin_mean_err, 0.0)
            push!(bin_std_err,  0.0)
            push!(bin_counts,   0)
        end
    end

    is_increasing = all(
        bin_mean_err[i] <= bin_mean_err[i+1]
        for i in 1:(length(bin_mean_err)-1)
        if bin_counts[i] > 0 && bin_counts[i+1] > 0
    )

    interp = if abs(corr) < 0.3
        "Weak or no correlation between complexity and error."
    elseif corr > 0.3
        "Positive correlation ($(round(corr;digits=2))): errors increase with complexity. " *
        "This suggests the judge struggles more with complex cases."
    else
        "Negative correlation ($(round(corr;digits=2))): errors decrease with complexity. " *
        "This is unusual and may indicate over-confidence on simple cases."
    end

    return Dict{String,Any}(
        "complexity_error_correlation" => corr,
        "correlation_p_value"          => p_value,
        "correlation_significant"      => p_value < 0.05,
        "bins" => Dict{String,Any}(
            "centers"     => centers,
            "mean_errors" => bin_mean_err,
            "std_errors"  => bin_std_err,
            "counts"      => bin_counts,
        ),
        "monotonic_increasing" => is_increasing,
        "interpretation"       => interp,
    )
end


# ---------------------------------------------------------------------------
# calculate_evs
# ---------------------------------------------------------------------------

"""
    calculate_evs(stability, fairness, polarization) -> Float64

Ethical Viability Score (EVS).

Harmonic mean of Stability and Fairness, penalised by Polarization.

    EVS = (2 · Stability · Fairness) / (Stability + Fairness) · (1 − Polarization)

All three inputs are expected in [0, 1].  Returns a value in [0, 1].
"""
function calculate_evs(
    stability    :: Float64,
    fairness     :: Float64,
    polarization :: Float64,
) :: Float64

    (stability + fairness) == 0 && return 0.0
    harmonic = 2.0 * stability * fairness / (stability + fairness)
    return harmonic * (1.0 - clamp(polarization, 0.0, 1.0))
end


# ---------------------------------------------------------------------------
# compute_stability_metric
# ---------------------------------------------------------------------------

"""
    compute_stability_metric(E_x, x_values; target_exponent=0.5) -> Float64

Goodness-of-fit to |E(x)| ≤ C · x^α (ERH boundary, with α fixed to
`target_exponent`).  Returns R² ∈ [0, 1]; higher = more stable.

Internal helper used by dual-metrics logic in the Python statistics module.
"""
function compute_stability_metric(
    E_x             :: Vector{Float64},
    x_values        :: Vector{<:Real};
    target_exponent :: Float64 = 0.5,
) :: Float64

    abs_E = abs.(E_x)
    xf    = Float64.(x_values)
    valid = (abs_E .> 0) .& (xf .> 1)
    count(valid) < 3 && return 0.0

    x    = xf[valid]
    y    = abs_E[valid]
    lx   = log.(x)
    ly   = log.(y)

    log_C  = mean(ly .- target_exponent .* lx)
    y_pred = exp.(log_C .+ target_exponent .* lx)

    ss_res = sum((y .- y_pred) .^ 2)
    ss_tot = sum((y .- mean(y)) .^ 2)

    r2 = ss_tot > 0 ? 1.0 - ss_res / ss_tot : 0.0
    return clamp(r2, 0.0, 1.0)
end


# ---------------------------------------------------------------------------
# calculate_von_neumann_entropy
# ---------------------------------------------------------------------------

"""
    calculate_von_neumann_entropy(density_matrix) -> Float64

Von Neumann entropy of a density matrix (social complexity measure).

    H(ρ) = −Tr(ρ · ln ρ)

High value indicates high social entanglement (complex dependencies);
zero indicates complete individual autonomy.

`density_matrix` must be Hermitian, positive semi-definite, with trace ≈ 1.
"""
function calculate_von_neumann_entropy(
    density_matrix :: Matrix{Float64},
) :: Float64

    eigenvals = real.(eigvals(Symmetric(density_matrix)))
    eigenvals = clamp.(eigenvals, 1e-15, 1.0)
    return Float64(-sum(eigenvals .* log.(eigenvals)))
end

# Accept complex Hermitian matrix
calculate_von_neumann_entropy(rho::Matrix{ComplexF64}) =
    calculate_von_neumann_entropy(real.(rho))


# ===========================================================================
# Private helpers
# ===========================================================================

"""
Ordinary least squares: fit y = a·x + b, return (a, b).
"""
function _ols(x::Vector{Float64}, y::Vector{Float64}) :: Tuple{Float64,Float64}
    n   = length(x)
    sx  = sum(x);   sy  = sum(y)
    sxx = sum(x .* x);  sxy = sum(x .* y)
    denom = n * sxx - sx^2
    denom == 0 && return (0.0, mean(y))
    a = (n * sxy - sx * sy) / denom
    b = (sy - a * sx) / n
    return a, b
end


"""
Fit degree-`d` polynomial to (x, y) using least squares.
Returns coefficients [c_d, c_{d-1}, ..., c_0] (highest-degree first).
"""
function _polyfit(x::Vector{Float64}, y::Vector{Float64}, d::Int) :: Vector{Float64}
    n = length(x)
    V = [x[i]^j for i in 1:n, j in 0:d]   # Vandermonde (ascending degree)
    coeffs_asc = V \ y
    return reverse(coeffs_asc)              # convert to descending (numpy convention)
end


"""
Evaluate polynomial with descending coefficients at each x.
"""
function _polyval(coeffs::Vector{Float64}, x::Vector{Float64}) :: Vector{Float64}
    d = length(coeffs) - 1
    return [sum(coeffs[j+1] * xi^(d-j) for j in 0:d) for xi in x]
end


"""
Build a result dict from model fit.  `extra` is merged in.
"""
function _result_dict(
    model_name :: Symbol,
    y          :: Vector{Float64},
    y_pred     :: Vector{Float64},
    x          :: Vector{Float64};
    extra...
) :: Dict{String, Any}

    ss_res  = sum((y .- y_pred) .^ 2)
    ss_tot  = sum((y .- mean(y)) .^ 2)
    r2      = ss_tot > 0 ? 1.0 - ss_res / ss_tot : 0.0
    rmse    = sqrt(mean((y .- y_pred) .^ 2))

    d = Dict{String,Any}(
        "model"      => string(model_name),
        "r_squared"  => r2,
        "rmse"       => rmse,
        "num_points" => length(x),
    )
    for (k, v) in extra
        d[string(k)] = v
    end
    return d
end


"""
Pearson correlation coefficient and two-tailed p-value (approximate, using
t-distribution with n-2 degrees of freedom via the Beta CDF approximation).
"""
function _pearsonr(x::Vector{Float64}, y::Vector{Float64}) :: Tuple{Float64,Float64}
    n  = length(x)
    n < 3 && return (NaN, NaN)
    r  = cor(x, y)
    # t-statistic
    t  = r * sqrt(n - 2) / sqrt(max(1 - r^2, 1e-15))
    # Approximate two-tailed p-value via regularised incomplete beta
    p  = _approx_t_pvalue(t, n - 2)
    return r, p
end


"""
Very simple two-tailed p-value for a t-statistic with `df` degrees of freedom.
Uses the normal approximation when df > 30 and a simple rational approximation
for df ≤ 30.  Accurate to ~3 significant figures — sufficient for the
"significant at 0.05" test used by `detect_structural_bias`.
"""
function _approx_t_pvalue(t::Float64, df::Int) :: Float64
    abs_t = abs(t)
    if df > 30
        # Normal approximation
        z = abs_t
        p_one = 0.5 * erfc(z / sqrt(2.0))
    else
        # Simple rational approximation for cumulative t (Abramowitz & Stegun 26.7)
        x2 = df / (df + t^2)
        # incomplete beta I_{x2}(df/2, 1/2) ≈ regularised beta function
        p_one = 0.5 * _regularised_ibeta(x2, df / 2.0, 0.5)
    end
    return min(1.0, 2 * p_one)
end

# erfc approximation (max error ~1.5e-7, Abramowitz & Stegun 7.1.26)
function erfc(x::Float64) :: Float64
    x < 0 && return 2.0 - erfc(-x)
    t  = 1.0 / (1.0 + 0.3275911 * x)
    p  = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 +
         t * (-1.453152027 + t * 1.061405429))))
    return p * exp(-x^2)
end

# Regularised incomplete Beta function via continued fraction (Lentz's method)
# Approximation — valid for 0 < x < 1, a > 0, b > 0.
function _regularised_ibeta(x::Float64, a::Float64, b::Float64) :: Float64
    (x <= 0) && return 0.0
    (x >= 1) && return 1.0
    # Use symmetry relation when needed for stability
    if x > (a + 1) / (a + b + 2)
        return 1.0 - _regularised_ibeta(1 - x, b, a)
    end
    lbeta   = lgamma(a) + lgamma(b) - lgamma(a + b)
    front   = exp(a * log(x) + b * log(1 - x) - lbeta) / a
    # Continued fraction (Lentz, 3 convergents — sufficient here)
    cf = _ibeta_cf(x, a, b)
    return front * cf
end

function _ibeta_cf(x::Float64, a::Float64, b::Float64; max_iter::Int = 200) :: Float64
    tiny = 1e-30
    f = tiny;  C = f;  D = 0.0
    for m in 0:max_iter
        for pm in (0, 1)  # even (pm=0) and odd (pm=1) numerators
            if m == 0 && pm == 0
                d = 1.0
            elseif pm == 0  # even step
                d =  m * (b - m) * x / ((a + 2m - 1) * (a + 2m))
            else            # odd step
                d = -(a + m) * (a + b + m) * x / ((a + 2m) * (a + 2m + 1))
            end
            D = 1.0 + d * D;  abs(D) < tiny && (D = tiny)
            C = 1.0 + d / C;  abs(C) < tiny && (C = tiny)
            D = 1.0 / D
            f *= C * D
            abs(C * D - 1.0) < 3e-7 && return f
        end
    end
    return f
end

function lgamma(x::Float64) :: Float64
    # Stirling approximation — sufficient for our uses (df/2, b=0.5, a≥1)
    x < 1 && return lgamma(x + 1) - log(x)
    return (x - 0.5) * log(x) - x + 0.5 * log(2π) +
           1/(12x) - 1/(360x^3) + 1/(1260x^5)
end


"""
Empirical quantile of a Float64 vector (linear interpolation).
"""
function _quantile(v::Vector{Float64}, q::Float64) :: Float64
    sv = sort(v)
    n  = length(sv)
    idx = 1 + q * (n - 1)
    lo  = floor(Int, idx);  hi = min(lo + 1, n)
    frac = idx - lo
    return sv[lo] * (1 - frac) + sv[hi] * frac
end

end  # module ERHStatistics
