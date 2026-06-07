"""
    ERHChecks

Julia implementation of the ERH consistency-check module.

Mirrors erh_core/analysis/erh_checks.py.

Centralises the operational definition of when a simulated system
"satisfies" the Ethical Riemann Hypothesis (ERH) style bound

    |E(x)| ≤ C · x^(1/2 + ε)

for configurable constants C, ε > 0.  Finite-sample slack is provided via

1. A multiplicative slack factor on the bound (e.g. 1.5×), and
2. A small allowed fraction of x-values where the bound can be slightly
   violated.

All high-level reporting should use these functions so the ERH decision
logic stays consistent across the codebase.
"""
module ERHChecks

export ERHCheckResult
export check_erh_bound
export check_erh_bound_structured

# ---------------------------------------------------------------------------
# ERHCheckResult — typed counterpart to the Python @dataclass
# ---------------------------------------------------------------------------

"""
    ERHCheckResult

Structured result from an ERH bound check.

Fields
------
- `erh_satisfied`       : overall verdict
- `violation_rate`      : fraction of x with |E(x)| > C·x^(1/2+ε)
- `bound_value`         : max C·x^(1/2+ε) across valid x
- `max_ratio`           : max |E(x)| / (C·x^(1/2+ε))
- `num_points`          : number of valid (x, E(x)) pairs
- `confidence_level`    : 1 − allowed_violation_rate
- `sample_size`         : alias for num_points
- `bound_type`          : e.g. `"erh_slack_1.5"` or `"erh_strict"`
- `C`                   : constant used in the bound
- `epsilon`             : exponent shift used in the bound
- `slack_factor`        : practical multiplier on the theoretical bound
- `judge_name`          : optional provenance label
"""
struct ERHCheckResult
    erh_satisfied    :: Bool
    violation_rate   :: Float64
    bound_value      :: Float64
    max_ratio        :: Float64
    num_points       :: Int
    confidence_level :: Float64
    sample_size      :: Int
    bound_type       :: String
    C                :: Float64
    epsilon          :: Float64
    slack_factor     :: Float64
    judge_name       :: Union{String, Nothing}
end


# ---------------------------------------------------------------------------
# check_erh_bound
# ---------------------------------------------------------------------------

"""
    check_erh_bound(E_x, x_values;
                    C=1.0, epsilon=0.1, slack_factor=1.5,
                    allowed_violation_rate=0.05) -> Dict{String, Any}

Check whether E_x satisfies the ERH-style bound.

Parameters
----------
- `E_x`                     : error values on a 1-D grid of complexities.
- `x_values`                : corresponding complexity values (same length).
- `C`                       : ERH constant in the bound |E(x)| ≤ C·x^(1/2+ε).
- `epsilon`                 : small positive ε in the exponent.
- `slack_factor`            : practical slack multiplier (finite-sample).
- `allowed_violation_rate`  : max fraction of x-values allowed to violate the
                              theoretical (non-slacked) bound.

Returns a `Dict` with keys:
- `"erh_satisfied"`  : Bool
- `"max_ratio"`      : Float64 — max |E(x)| / (C·x^(1/2+ε))
- `"violation_rate"` : Float64 — fraction of x with |E(x)| > bound
- `"num_points"`     : Int

Throws `ArgumentError` on invalid parameter values.
"""
function check_erh_bound(
    E_x                    :: Vector{Float64},
    x_values               :: Vector{Float64};
    C                      :: Float64 = 1.0,
    epsilon                :: Float64 = 0.1,
    slack_factor           :: Float64 = 1.5,
    allowed_violation_rate :: Float64 = 0.05,
) :: Dict{String, Any}

    # --- Parameter validation ---
    C <= 0        && throw(ArgumentError("C must be positive, got C=$C."))
    epsilon < 0   && throw(ArgumentError("epsilon must be non-negative, got epsilon=$epsilon."))
    !(0.0 <= allowed_violation_rate <= 1.0) && throw(
        ArgumentError("allowed_violation_rate must be in [0,1], got $allowed_violation_rate."))
    slack_factor <= 0 && throw(ArgumentError("slack_factor must be positive, got $slack_factor."))

    if length(E_x) != length(x_values)
        throw(ArgumentError(
            "Shape mismatch: E_x has length $(length(E_x)) but x_values has length $(length(x_values))."))
    end

    # --- Valid mask: positive complexities, finite errors ---
    valid = (x_values .> 0) .& isfinite.(E_x) .& isfinite.(x_values)

    if !any(valid)
        return Dict{String,Any}(
            "erh_satisfied"  => false,
            "max_ratio"      => NaN,
            "violation_rate" => NaN,
            "num_points"     => 0,
        )
    end

    x    = x_values[valid]
    absE = abs.(E_x[valid])

    # Theoretical ERH bound
    erh_bound = C .* (x .^ (0.5 + epsilon))

    ratios = map(zip(absE, erh_bound)) do (ae, b)
        b > 0 ? ae / b : Inf
    end

    max_ratio      = maximum(ratios)
    num_pts        = count(valid)
    violation_mask = ratios .> 1.0
    violation_rate = num_pts > 0 ? mean(violation_mask) : NaN

    exceeds_slack  = max_ratio > slack_factor
    erh_satisfied  = (violation_rate <= allowed_violation_rate) && !exceeds_slack

    return Dict{String,Any}(
        "erh_satisfied"  => erh_satisfied,
        "max_ratio"      => max_ratio,
        "violation_rate" => violation_rate,
        "num_points"     => num_pts,
    )
end

# Convenience overload: accept Int vectors
check_erh_bound(E_x::Vector{Float64}, x_values::Vector{Int}; kw...) =
    check_erh_bound(E_x, Float64.(x_values); kw...)


# ---------------------------------------------------------------------------
# check_erh_bound_structured
# ---------------------------------------------------------------------------

"""
    check_erh_bound_structured(E_x, x_values;
                                C=1.0, epsilon=0.1, slack_factor=1.5,
                                allowed_violation_rate=0.05,
                                judge_name=nothing) -> ERHCheckResult

Typed wrapper around `check_erh_bound` returning an `ERHCheckResult` struct
with provenance metadata (confidence_level, bound_type, judge_name, etc.).
"""
function check_erh_bound_structured(
    E_x                    :: Vector{Float64},
    x_values               :: Vector{<:Real};
    C                      :: Float64              = 1.0,
    epsilon                :: Float64              = 0.1,
    slack_factor           :: Float64              = 1.5,
    allowed_violation_rate :: Float64              = 0.05,
    judge_name             :: Union{String,Nothing} = nothing,
) :: ERHCheckResult

    raw = check_erh_bound(
        E_x, Float64.(x_values);
        C = C, epsilon = epsilon,
        slack_factor = slack_factor,
        allowed_violation_rate = allowed_violation_rate,
    )

    # Compute max theoretical bound for the bound_value field
    x_arr   = Float64.(x_values)
    valid_x = x_arr[x_arr .> 0]
    bound_value = isempty(valid_x) ? NaN : maximum(C .* (valid_x .^ (0.5 + epsilon)))

    num_pts    = raw["num_points"]
    bound_type = slack_factor != 1.0 ? "erh_slack_$(slack_factor)" : "erh_strict"

    return ERHCheckResult(
        Bool(raw["erh_satisfied"]),
        Float64(raw["violation_rate"]),
        bound_value,
        Float64(raw["max_ratio"]),
        num_pts,
        1.0 - allowed_violation_rate,
        num_pts,
        bound_type,
        C,
        epsilon,
        slack_factor,
        judge_name,
    )
end

end  # module ERHChecks
