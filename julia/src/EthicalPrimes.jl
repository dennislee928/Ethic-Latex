"""
    EthicalPrimes

Julia implementation of the ethical primes module.

Mirrors erh_core/core/ethical_primes.py.

"Ethical primes" are structurally-critical misjudgments — the subset of mistakes
that are most important, fall in a meaningful complexity range, and cannot be
decomposed into simpler cases.  The module also computes Π(x), B(x), and
E(x) = Π(x) − B(x), which are the core quantities for the Ethical Riemann
Hypothesis (ERH) analogy.
"""
module EthicalPrimes

using Statistics: median, mean, std, var
using LinearAlgebra: norm

export Action
export select_ethical_primes
export compute_Pi_and_error
export compute_error_correction_impact
export analyze_error_growth
export compute_prime_density

# ---------------------------------------------------------------------------
# Action struct — minimal analogue of the Python Action dataclass
# ---------------------------------------------------------------------------

"""
    Action

Minimal representation of a judged action.

Fields
------
- `c`            : complexity (integer ≥ 1)
- `w`            : importance weight (≥ 0)
- `V`            : ground-truth moral value
- `J`            : judge's assessment (nothing if not yet judged)
- `delta`        : error J − V (nothing if not judged)
- `mistake_flag` : 1 if |delta| > tau, 0 otherwise (nothing if not judged)
- `group`        : optional group label for fairness analysis
"""
mutable struct Action
    c            :: Int
    w            :: Float64
    V            :: Float64
    J            :: Union{Float64, Nothing}
    delta        :: Union{Float64, Nothing}
    mistake_flag :: Union{Int, Nothing}
    group        :: Union{String, Nothing}
end

# Convenience constructor — only the required fields.
Action(c::Int, w::Float64, V::Float64) =
    Action(c, w, V, nothing, nothing, nothing, nothing)

# ---------------------------------------------------------------------------
# select_ethical_primes
# ---------------------------------------------------------------------------

"""
    select_ethical_primes(actions; importance_quantile=0.9, strategy=:importance,
                          complexity_range=nothing) -> Vector{Action}

Select "ethical primes" from the set of misjudged actions.

Ethical primes are defined as critical misjudgments — cases that:
1. Are actually misjudged (`mistake_flag == 1`)
2. Have high importance (`w` above the given quantile)
3. Fall within a meaningful complexity range

Parameters
----------
- `importance_quantile` : keep only the top `(1 - quantile)` fraction by importance.
- `strategy`            : `:importance`, `:complexity`, or `:hybrid`.
- `complexity_range`    : `(min_c, max_c)` tuple; auto-computed if `nothing`.

Reference: Paper §3, Definition 3.1 (Ethical Primes).
"""
function select_ethical_primes(
    actions              :: Vector{Action};
    importance_quantile  :: Float64          = 0.9,
    strategy             :: Symbol           = :importance,
    complexity_range     :: Union{Tuple{Int,Int}, Nothing} = nothing,
) :: Vector{Action}

    # Filter to misjudgments
    mistakes = [a for a in actions if !isnothing(a.mistake_flag) && a.mistake_flag == 1]

    isempty(mistakes) && return Action[]

    # Apply complexity range filter
    if !isnothing(complexity_range)
        min_c, max_c = complexity_range
        mistakes = [a for a in mistakes if min_c <= a.c <= max_c]
    else
        # Auto range: exclude bottom 10 % and top 10 % complexity
        all_c = sort([a.c for a in mistakes])
        n = length(all_c)
        if n >= 10
            min_c = all_c[max(1, n ÷ 10 + 1)]
            max_c = all_c[min(n, 9 * n ÷ 10)]
            mistakes = [a for a in mistakes if min_c <= a.c <= max_c]
        end
    end

    isempty(mistakes) && return Action[]

    cutoff(lst) = max(1, round(Int, length(lst) * (1 - importance_quantile)))

    if strategy == :importance
        sort!(mistakes; by = a -> a.w, rev = true)
        return mistakes[1:cutoff(mistakes)]

    elseif strategy == :complexity
        complexities = Float64[a.c for a in mistakes]
        med_c = median(complexities)
        max_w = max(maximum(a.w for a in mistakes), 1e-9)

        score(a) = begin
            c_score = 1.0 / (1.0 + abs(a.c - med_c) / (med_c == 0 ? 1.0 : med_c))
            w_score = a.w / max_w
            0.3 * c_score + 0.7 * w_score
        end

        sort!(mistakes; by = score, rev = true)
        return mistakes[1:cutoff(mistakes)]

    elseif strategy == :hybrid
        max_w     = max(maximum(a.w for a in mistakes), 1e-9)
        max_delta = max(maximum(abs(a.delta === nothing ? 0.0 : a.delta) for a in mistakes), 1e-9)

        score(a) = begin
            w_n = a.w / max_w
            d_n = (isnothing(a.delta) ? 0.0 : abs(a.delta)) / max_delta
            0.7 * w_n + 0.3 * d_n
        end

        sort!(mistakes; by = score, rev = true)
        return mistakes[1:cutoff(mistakes)]

    else
        throw(ArgumentError("Unknown strategy: $strategy.  Use :importance, :complexity, or :hybrid."))
    end
end


# ---------------------------------------------------------------------------
# compute_Pi_and_error
# ---------------------------------------------------------------------------

"""
    compute_Pi_and_error(primes; X_max=100, baseline=:prime_theorem,
                         baseline_params=nothing)
          -> (Pi_x, B_x, E_x, x_values)

Compute Π(x), B(x), and E(x) = Π(x) − B(x).

Supported `baseline` symbols
-----------------------------
- `:linear`          — B(x) = α · x          (param: `alpha`, default 0.1)
- `:prime_theorem`   — B(x) = β · x / log(x) (param: `beta`,  default 1.0)
- `:power_law`       — B(x) = γ · x^δ        (params: `gamma`, `delta`)
- `:fitted`          — degree-3 polynomial fit to Π(x)

Reference: Paper §4, Definitions 4.1–4.3.
"""
function compute_Pi_and_error(
    primes         :: Vector{Action};
    X_max          :: Int            = 100,
    baseline       :: Symbol         = :prime_theorem,
    baseline_params :: Union{Dict, Nothing} = nothing,
) :: Tuple{Vector{Float64}, Vector{Float64}, Vector{Float64}, Vector{Int}}

    x_values = collect(1:X_max)

    # ------------------------------------------------------------------
    # Compute Π(x) : count of ethical primes with complexity ≤ x
    # ------------------------------------------------------------------
    prime_c = Float64[p.c for p in primes if p.c <= X_max]

    Pi_x = if isempty(prime_c)
        zeros(Float64, X_max)
    else
        # Vectorised: for each x, sum(c_i <= x)
        Float64[count(c -> c <= Float64(x), prime_c) for x in x_values]
    end

    # ------------------------------------------------------------------
    # Compute B(x)
    # ------------------------------------------------------------------
    params = isnothing(baseline_params) ? Dict{String,Float64}() : baseline_params

    B_x = if baseline == :linear
        alpha = get(params, "alpha", 0.1)
        alpha .* Float64.(x_values)

    elseif baseline == :prime_theorem
        beta = get(params, "beta", 1.0)
        # B(1) = 0  (log(1) = 0 → undefined → set to 0)
        [x == 1 ? 0.0 : beta * x / log(x) for x in x_values]

    elseif baseline == :power_law
        gamma = get(params, "gamma", 0.1)
        delta = get(params, "delta", 1.0)
        gamma .* Float64.(x_values) .^ delta

    elseif baseline == :fitted
        if length(primes) < 5
            0.1 .* Float64.(x_values)
        else
            degree = min(3, length(primes) ÷ 2)
            _polyfit_eval(Float64.(x_values), Pi_x, degree)
        end

    else
        throw(ArgumentError("Unknown baseline: $baseline.  Use :linear, :prime_theorem, :power_law, or :fitted."))
    end

    E_x = Pi_x .- B_x

    return Pi_x, B_x, E_x, x_values
end


# ---------------------------------------------------------------------------
# compute_error_correction_impact
# ---------------------------------------------------------------------------

"""
    compute_error_correction_impact(actions, mistake_indices; tau=0.3)
          -> Dict{Int, Float64}

Estimate the impact of correcting each mistake on the global error rate.

Reference: Paper §3 (structural fundamentality of a prime).
"""
function compute_error_correction_impact(
    actions         :: Vector{Action},
    mistake_indices :: Vector{Int};
    tau             :: Float64 = 0.3,
) :: Dict{Int, Float64}

    total_errors = count(a -> !isnothing(a.mistake_flag) && a.mistake_flag == 1, actions)
    n = length(actions)
    baseline_error_rate = n > 0 ? total_errors / n : 0.0

    impacts = Dict{Int, Float64}()

    for idx in mistake_indices
        idx > n && continue
        action = actions[idx]

        if isnothing(action.mistake_flag) || action.mistake_flag == 0
            impacts[idx] = 0.0
            continue
        end

        error_magnitude = isnothing(action.delta) ? 0.0 : abs(action.delta)

        # Count structurally similar mistakes
        similar_count = 0
        for other in actions
            other === action && continue
            (!isnothing(other.mistake_flag) && other.mistake_flag == 1) || continue

            c_denom  = max(action.c, other.c, 1)
            w_denom  = max(action.w, other.w, 0.001)
            c_diff   = abs(action.c - other.c) / c_denom
            w_diff   = abs(action.w - other.w) / w_denom

            if c_diff < 0.2 && w_diff < 0.2
                similar_count += 1
            end
        end

        estimated_reduction = action.w * error_magnitude * (1.0 + 0.1 * similar_count)

        impact = if baseline_error_rate > 0
            min(1.0, estimated_reduction / (baseline_error_rate * n))
        else
            0.0
        end

        impacts[idx] = impact
    end

    return impacts
end


# ---------------------------------------------------------------------------
# analyze_error_growth
# ---------------------------------------------------------------------------

"""
    analyze_error_growth(E_x, x_values; expected_exponent=0.5) -> Dict

Analyse whether |E(x)| grows like x^α and estimate α via log-log regression.

The ERH hypothesis predicts α ≈ 0.5.

Returns a `Dict` with keys:
- `estimated_exponent`  : fitted α
- `constant_C`          : fitted C in |E(x)| ≈ C · x^α
- `erh_satisfied`       : bool (bound-based, from `ERHChecks`)
- `r_squared`           : R² of the log-log fit
- `max_absolute_error`  : max |E(x)|
- `mean_absolute_error` : mean |E(x)|
- `growth_rate`         : qualitative label
- `deviation_from_erh`  : |α − 0.5|

Reference: Paper §6 (Error Growth Analysis).
"""
function analyze_error_growth(
    E_x              :: Vector{Float64},
    x_values         :: Vector{Int};
    expected_exponent :: Float64 = 0.5,
) :: Dict{String, Any}

    abs_E      = abs.(E_x)
    x_float    = Float64.(x_values)
    valid_mask = (abs_E .> 0) .& (x_float .> 1)

    max_abs_err  = isempty(abs_E) ? 0.0 : maximum(abs_E)
    mean_abs_err = isempty(abs_E) ? 0.0 : mean(abs_E)

    if count(valid_mask) < 5
        return Dict{String,Any}(
            "estimated_exponent"  => NaN,
            "constant_C"          => NaN,
            "erh_satisfied"       => false,
            "r_squared"           => 0.0,
            "max_absolute_error"  => max_abs_err,
            "mean_absolute_error" => mean_abs_err,
            "growth_rate"         => "insufficient_data",
            "deviation_from_erh"  => NaN,
            "erh_max_ratio"       => NaN,
            "erh_violation_rate"  => NaN,
        )
    end

    x_v = x_float[valid_mask]
    E_v = abs_E[valid_mask]

    log_x = log.(x_v)
    log_E = log.(E_v)

    # Linear regression in log space: log|E| = log(C) + α·log(x)
    alpha, log_C = _linear_regression(log_x, log_E)
    C = exp(log_C)

    # R² in log space
    log_E_pred = log_C .+ alpha .* log_x
    ss_res = sum((log_E .- log_E_pred) .^ 2)
    ss_tot = sum((log_E .- mean(log_E)) .^ 2)
    r2 = ss_tot > 0 ? 1.0 - ss_res / ss_tot : 0.0

    # ERH bound check (delegate to ERHChecks when available; inline here)
    bound_stats = _check_erh_bound_inline(E_x, x_float)

    deviation = abs(alpha - expected_exponent)

    growth_rate = if alpha < 0.4
        "sublinear_slow"
    elseif alpha < 0.6
        "square_root"
    elseif alpha < 0.9
        "sublinear_fast"
    elseif alpha < 1.1
        "linear"
    else
        "superlinear"
    end

    return Dict{String,Any}(
        "estimated_exponent"  => alpha,
        "constant_C"          => C,
        "erh_satisfied"       => bound_stats["erh_satisfied"],
        "r_squared"           => r2,
        "max_absolute_error"  => max_abs_err,
        "mean_absolute_error" => mean_abs_err,
        "growth_rate"         => growth_rate,
        "deviation_from_erh"  => deviation,
        "erh_max_ratio"       => bound_stats["max_ratio"],
        "erh_violation_rate"  => bound_stats["violation_rate"],
    )
end


# ---------------------------------------------------------------------------
# compute_prime_density
# ---------------------------------------------------------------------------

"""
    compute_prime_density(primes; X_max=100, bin_size=5)
          -> (bin_centers, densities)

Compute the density of ethical primes in complexity bins.
"""
function compute_prime_density(
    primes   :: Vector{Action};
    X_max    :: Int = 100,
    bin_size :: Int = 5,
) :: Tuple{Vector{Float64}, Vector{Int}}

    edges       = collect(0:bin_size:X_max)
    n_bins      = length(edges) - 1
    bin_centers = Float64[(edges[i] + edges[i+1]) / 2.0 for i in 1:n_bins]

    prime_c  = [p.c for p in primes if p.c <= X_max]
    densities = zeros(Int, n_bins)

    for c in prime_c
        for b in 1:n_bins
            if edges[b] < c <= edges[b+1]
                densities[b] += 1
                break
            end
        end
    end

    return bin_centers, densities
end


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

"""
Ordinary least squares: fit y = a·x + b, return (a, b).
"""
function _linear_regression(x::Vector{Float64}, y::Vector{Float64})
    n  = length(x)
    sx = sum(x);  sy = sum(y)
    sxx = sum(x .* x);  sxy = sum(x .* y)
    denom = n * sxx - sx^2
    denom == 0 && return (0.0, mean(y))
    a = (n * sxy - sx * sy) / denom
    b = (sy - a * sx) / n
    return a, b
end


"""
Inline ERH bound check (mirrors ERHChecks.check_erh_bound with default params).
Used inside EthicalPrimes to avoid a circular include dependency.
"""
function _check_erh_bound_inline(
    E_x      :: Vector{Float64},
    x_values :: Vector{Float64};
    C        :: Float64 = 1.0,
    epsilon  :: Float64 = 0.1,
    slack    :: Float64 = 1.5,
    avr      :: Float64 = 0.05,
) :: Dict{String, Any}

    valid = (x_values .> 0) .& isfinite.(E_x) .& isfinite.(x_values)
    if !any(valid)
        return Dict{String,Any}("erh_satisfied" => false,
                                "max_ratio"      => NaN,
                                "violation_rate" => NaN,
                                "num_points"     => 0)
    end

    x    = x_values[valid]
    absE = abs.(E_x[valid])
    bound  = C .* (x .^ (0.5 + epsilon))
    ratios = bound .> 0 ? absE ./ bound : fill(Inf, length(absE))

    max_ratio       = maximum(ratios)
    violation_rate  = mean(ratios .> 1.0)
    erh_satisfied   = (violation_rate <= avr) && (max_ratio <= slack)

    return Dict{String,Any}(
        "erh_satisfied"  => erh_satisfied,
        "max_ratio"      => max_ratio,
        "violation_rate" => violation_rate,
        "num_points"     => count(valid),
    )
end


"""
Fit a degree-`d` polynomial to `y` evaluated at `x`, return fitted values.
Uses normal equations via least squares (Vandermonde matrix).
"""
function _polyfit_eval(
    x :: Vector{Float64},
    y :: Vector{Float64},
    d :: Int,
) :: Vector{Float64}

    n = length(x)
    V = [x[i]^j for i in 1:n, j in 0:d]          # Vandermonde
    coeffs = V \ y                                  # least-squares solution
    return [sum(coeffs[j+1] * x[i]^j for j in 0:d) for i in 1:n]
end

end  # module EthicalPrimes
