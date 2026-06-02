"""
    TemporalERH — Temporal extension of the Ethical Riemann Hypothesis.

    Mirrors erh_core/core/temporal_erh.py in Julia.

    Key quantities:
    - Π(x,t)  : count of ethical primes with complexity ≤ x at time t
    - B(x,t)  : baseline expectation (prime-theorem style)
    - E(x,t)  = Π(x,t) − B(x,t)

    Additional capabilities:
    - Stochastic perturbation (Ornstein-Uhlenbeck-style correlated noise)
    - Mule-effect injection (sudden anomalies analogous to Asimov's Mule)
    - Anomaly detection against ERH bounds
"""
module TemporalERH

using Statistics
using Random
using LinearAlgebra

export compute_Pi_temporal, compute_E_temporal, compute_baseline_temporal,
       track_error_evolution, simulate_mule_effect, detect_mule_anomalies,
       add_stochastic_perturbation

# ---------------------------------------------------------------------------
# Lightweight action type (shared with ABMSimulator)
# ---------------------------------------------------------------------------

"""
    TAction

Minimal complexity-bearing action struct used inside this module.
Callers that already have their own action type should convert before calling.
"""
struct TAction
    id::Int
    c::Float64
    V::Float64
    w::Float64
end

# ---------------------------------------------------------------------------
# Π(x,t)
# ---------------------------------------------------------------------------

"""
    compute_Pi_temporal(primes_history, time_steps, X_max=100) → Matrix{Float64}

Compute Π(x,t) array of shape `(time_steps, X_max)`.

`primes_history[t]` is a `Vector` of actions (any type with a field `.c`) at
time step t (1-indexed in Julia).
"""
function compute_Pi_temporal(
    primes_history::Vector{<:Vector},
    time_steps::Int,
    X_max::Int=100
)::Matrix{Float64}
    Pi_xt = zeros(Float64, time_steps, X_max)
    for t in 1:time_steps
        t > length(primes_history) && break
        primes_t = primes_history[t]
        for x in 1:X_max
            Pi_xt[t, x] = count(p -> p.c <= x, primes_t)
        end
    end
    return Pi_xt
end

# ---------------------------------------------------------------------------
# B(x,t) baseline
# ---------------------------------------------------------------------------

"""
    compute_baseline_temporal(time_steps, X_max=100; baseline_type, baseline_params,
                               time_dependent) → Matrix{Float64}

Supported `baseline_type` values:
- `"prime_theorem"` (default): B = β·x/log(x)
- `"linear"`:                  B = α·x
- `"logarithmic_integral"`:    B = β·x/log(x)  (same approximation)
- `"power_law"`:               B = γ·x^δ
"""
function compute_baseline_temporal(
    time_steps::Int,
    X_max::Int=100;
    baseline_type::String="prime_theorem",
    baseline_params::Dict{String,Float64}=Dict{String,Float64}(),
    time_dependent::Bool=false
)::Matrix{Float64}
    B_xt  = zeros(Float64, time_steps, X_max)
    x_vals = 1:X_max

    # Default parameter values
    defaults = Dict(
        "prime_theorem"        => Dict("beta"  => 10.0),
        "linear"               => Dict("alpha" => 0.1),
        "logarithmic_integral" => Dict("beta"  => 8.0),
        "power_law"            => Dict("gamma" => 0.5, "delta" => 0.8)
    )
    params = merge(get(defaults, baseline_type, Dict{String,Float64}()), baseline_params)

    for t in 1:time_steps
        time_factor = time_dependent ? 1.0 + 0.01 * (t - 1) / time_steps : 1.0

        if baseline_type == "linear"
            α = get(params, "alpha", 0.1)
            for x in x_vals; B_xt[t, x] = α * x * time_factor; end

        elseif baseline_type in ("prime_theorem", "logarithmic_integral")
            β = get(params, "beta", baseline_type == "prime_theorem" ? 10.0 : 8.0)
            for x in x_vals
                lx = log(max(x, 2))
                B_xt[t, x] = β * x / lx * time_factor
            end

        elseif baseline_type == "power_law"
            γ = get(params, "gamma", 0.5)
            δ = get(params, "delta", 0.8)
            for x in x_vals; B_xt[t, x] = γ * (x^δ) * time_factor; end
        end
    end
    return B_xt
end

# ---------------------------------------------------------------------------
# E(x,t)
# ---------------------------------------------------------------------------

"""
    compute_E_temporal(Pi_xt, B_xt, time_steps, X_max=100) → Matrix{Float64}

E(x,t) = Π(x,t) − B(x,t).
"""
function compute_E_temporal(
    Pi_xt::Matrix{Float64},
    B_xt::Matrix{Float64},
    time_steps::Int,
    X_max::Int=100
)::Matrix{Float64}
    return Pi_xt .- B_xt
end

# ---------------------------------------------------------------------------
# Track error evolution
# ---------------------------------------------------------------------------

"""
    track_error_evolution(actions_history, judge_fn; τ, time_steps, X_max,
                           importance_quantile) → Dict{String,Any}

`judge_fn(action, τ) → Bool` encodes whether an action is a misjudgment.

Returns Dict with keys: `"Pi_xt"`, `"B_xt"`, `"E_xt"`, `"primes_history"`,
`"time_steps"`, `"X_max"`.
"""
function track_error_evolution(
    actions_history::Vector{<:Vector},
    judge_fn::Function;
    τ::Float64=0.3,
    time_steps::Int=10,
    X_max::Int=100,
    importance_quantile::Float64=0.9
)::Dict{String,Any}
    primes_history = Vector[]
    n_steps = min(time_steps, length(actions_history))

    for t in 1:n_steps
        actions_t  = actions_history[t]
        judgments  = [judge_fn(a, τ) for a in actions_t]
        err_actions = actions_t[judgments]

        # Select top-importance error actions
        if !isempty(err_actions)
            weights = [a.w for a in err_actions]
            thresh  = quantile(weights, importance_quantile)
            primes  = filter(a -> a.w >= thresh, err_actions)
        else
            primes = eltype(actions_t)[]
        end
        push!(primes_history, primes)
    end

    Pi_xt = compute_Pi_temporal(primes_history, time_steps, X_max)
    B_xt  = compute_baseline_temporal(time_steps, X_max)
    E_xt  = compute_E_temporal(Pi_xt, B_xt, time_steps, X_max)

    return Dict{String,Any}(
        "Pi_xt"          => Pi_xt,
        "B_xt"           => B_xt,
        "E_xt"           => E_xt,
        "primes_history" => primes_history,
        "time_steps"     => time_steps,
        "X_max"          => X_max
    )
end

# ---------------------------------------------------------------------------
# Mule effect
# ---------------------------------------------------------------------------

"""
    simulate_mule_effect(E_xt, mule_time; mule_strength, mule_complexity_range,
                          X_max, seed) → Matrix{Float64}

Inject a sudden-spike anomaly at `mule_time` (1-indexed) over the specified
complexity range, with exponential-decay ripple to subsequent steps.
"""
function simulate_mule_effect(
    E_xt::Matrix{Float64},
    mule_time::Int;
    mule_strength::Float64=2.0,
    mule_complexity_range::Union{Tuple{Int,Int},Nothing}=nothing,
    X_max::Int=size(E_xt, 2),
    seed::Int=42
)::Matrix{Float64}
    rng           = Xoshiro(seed)
    E_modified    = copy(E_xt)
    time_steps, _ = size(E_xt)

    mule_time > time_steps && return E_modified

    min_c, max_c = mule_complexity_range === nothing ?
                   (X_max ÷ 3, X_max) : mule_complexity_range

    for x_idx in min_c:min(max_c, X_max)
        base_error  = E_xt[mule_time, x_idx]
        mule_error  = base_error * mule_strength
        direction   = rand(rng, [-1.0, 1.0])
        E_modified[mule_time, x_idx] = direction * abs(mule_error)
        # Ripple effect
        for t in (mule_time+1):min(mule_time+2, time_steps)
            decay_factor = 0.5^(t - mule_time)
            E_modified[t, x_idx] += direction * abs(mule_error) * decay_factor * 0.3
        end
    end
    return E_modified
end

# ---------------------------------------------------------------------------
# Anomaly detection
# ---------------------------------------------------------------------------

"""
    detect_mule_anomalies(E_xt; C, epsilon, threshold_multiplier, X_max)
        → Vector{Dict{String,Any}}

Detect entries where |E(x,t)| > threshold_multiplier · C · x^(½+ε).
Returns a list of anomaly dicts with keys: `"time"`, `"complexity"`,
`"error_magnitude"`, `"erh_bound"`, `"violation_ratio"`, `"error_value"`.
"""
function detect_mule_anomalies(
    E_xt::Matrix{Float64};
    C::Float64=1.0,
    epsilon::Float64=0.1,
    threshold_multiplier::Float64=1.5,
    X_max::Int=size(E_xt, 2)
)::Vector{Dict{String,Any}}
    anomalies   = Dict{String,Any}[]
    time_steps, nx = size(E_xt)

    for t in 1:time_steps, x_idx in 1:min(nx, X_max)
        x          = x_idx          # complexity value (1-indexed matches Python)
        error_mag  = abs(E_xt[t, x_idx])
        erh_bound  = C * (x ^ (0.5 + epsilon))
        threshold  = erh_bound * threshold_multiplier

        if error_mag > threshold
            push!(anomalies, Dict{String,Any}(
                "time"            => t - 1,   # 0-indexed for Python parity
                "complexity"      => x,
                "error_magnitude" => error_mag,
                "erh_bound"       => erh_bound,
                "violation_ratio" => error_mag / erh_bound,
                "error_value"     => E_xt[t, x_idx]
            ))
        end
    end
    return anomalies
end

# ---------------------------------------------------------------------------
# Stochastic perturbation (correlated noise)
# ---------------------------------------------------------------------------

"""
    add_stochastic_perturbation(E_xt; noise_scale, correlation_time, seed)
        → Matrix{Float64}

Add OU-process-style correlated noise to E_xt.
"""
function add_stochastic_perturbation(
    E_xt::Matrix{Float64};
    noise_scale::Float64=0.1,
    correlation_time::Int=2,
    seed::Int=42
)::Matrix{Float64}
    rng                = Xoshiro(seed)
    E_perturbed        = copy(E_xt)
    time_steps, X_max  = size(E_xt)
    noise              = zeros(Float64, time_steps, X_max)
    decay              = exp(-1.0 / correlation_time)

    for t in 1:time_steps
        if t == 1
            noise[1, :] = noise_scale .* randn(rng, X_max)
        else
            noise[t, :] = decay .* noise[t-1, :] .+
                          noise_scale * (1 - decay) .* randn(rng, X_max)
        end
    end
    E_perturbed .+= noise
    return E_perturbed
end

end # module TemporalERH
