"""
    ABMSimulator — Agent-Based Modeling simulator for the ERH framework.

    Mirrors erh_core/core/abm_simulator.py using Agents.jl v6 patterns.

    Key responsibilities:
    - Maintain a population of `EthicalAgentABM` agents on a `StandardABM`.
    - Drive time-stepped simulation, computing Π(x), B(x), E(x) at every step.
    - Expose calibration and summary helpers so Python callers (via PyJulia /
      the HTTP sidecar) can inspect results without extra translation.
"""
module ABMSimulator

using Agents
using Statistics
using LinearAlgebra
using Random

export EthicalAgentABM, ABMSimulatorState,
       create_simulator, run_simulation!, compute_temporal_erh,
       calibrate_erh_parameters, get_simulation_summary

# ---------------------------------------------------------------------------
# Agent definition (Agents.jl ≥ 6 @agent macro)
# ---------------------------------------------------------------------------

@agent struct EthicalAgentABM(NoSpaceAgent)
    bias_strength::Float64        # analogous to BiasedJudge bias_strength
    error_rate::Float64           # running error rate [0,1]
    judgment_tendency::Float64    # opinion value (used by opinion dynamics)
    num_judgments::Int            # total judgments made
end

# ---------------------------------------------------------------------------
# Lightweight action representation (no dependency on erh_core)
# ---------------------------------------------------------------------------

"""
    SimAction

Minimal struct mirroring erh_core Action: id, complexity c, value V, weight w.
"""
struct SimAction
    id::Int
    c::Float64   # complexity
    V::Float64   # value
    w::Float64   # weight (importance)
end

# ---------------------------------------------------------------------------
# Helper: generate a random world of actions
# ---------------------------------------------------------------------------

"""
    generate_world(num_actions; rng) → Vector{SimAction}

Generate `num_actions` synthetic actions with random complexity, value and weight.
"""
function generate_world(num_actions::Int; rng::AbstractRNG=Random.default_rng())
    [SimAction(
        i,
        1.0 + 99.0 * rand(rng),   # complexity ∈ [1, 100]
        rand(rng),                  # value ∈ [0, 1]
        0.5 + rand(rng)             # weight ∈ [0.5, 1.5]
    ) for i in 1:num_actions]
end

# ---------------------------------------------------------------------------
# Judge logic (simplified analog of BiasedJudge)
# ---------------------------------------------------------------------------

"""
    judge_action(agent, action, τ) → Bool

Returns `true` if the agent considers `action` a misjudgment (i.e. error).
Biased judge: probability of error ≈ bias_strength scaled by action value.
"""
function judge_action(agent::EthicalAgentABM, action::SimAction, τ::Float64)
    noise = agent.bias_strength * (1.0 - action.V)
    return noise > τ
end

# ---------------------------------------------------------------------------
# Ethical primes selection
# ---------------------------------------------------------------------------

"""
    select_ethical_primes(actions, judgments; importance_quantile=0.9) → Vector{SimAction}

Select actions that were judged as errors AND have high importance weight.
These are the "ethical primes" — the most significant misjudgments.
"""
function select_ethical_primes(
    actions::Vector{SimAction},
    judgments::Vector{Bool};
    importance_quantile::Float64=0.9
)
    error_actions = actions[judgments]
    isempty(error_actions) && return SimAction[]
    weights = [a.w for a in error_actions]
    thresh = quantile(weights, importance_quantile)
    return filter(a -> a.w >= thresh, error_actions)
end

# ---------------------------------------------------------------------------
# ERH metrics: Π(x), B(x), E(x)
# ---------------------------------------------------------------------------

"""
    compute_Pi_and_error(primes, X_max) → (Pi_x, B_x, E_x, x_vals)

Compute:
- `Pi_x[i]` = count of primes with complexity ≤ x_vals[i]
- `B_x[i]`  = baseline B(x) ≈ β · x / log(x)  (Prime-Theorem-style)
- `E_x[i]`  = Pi_x[i] − B_x[i]
"""
function compute_Pi_and_error(
    primes::Vector{SimAction},
    X_max::Int=100;
    beta::Float64=10.0
)
    x_vals = collect(1:X_max)
    Pi_x   = Float64[count(p -> p.c <= x, primes) for x in x_vals]
    B_x    = Float64[beta * x / max(log(x), 1e-10) for x in x_vals]
    E_x    = Pi_x .- B_x
    return Pi_x, B_x, E_x, x_vals
end

"""
    analyze_error_growth(E_x, x_vals) → NamedTuple

Fit log|E(x)| ~ α + γ·log(x) to estimate the error exponent γ.
Returns `erh_satisfied = true` when γ ≤ 0.5 + 0.01`.
"""
function analyze_error_growth(E_x::Vector{Float64}, x_vals::Vector{Int})
    abs_E = abs.(E_x)
    pos   = findall(v -> v > 0, abs_E)
    if length(pos) < 3
        return (erh_satisfied=false, estimated_exponent=NaN, num_primes=length(E_x))
    end
    log_x = log.(x_vals[pos])
    log_E = log.(abs_E[pos])
    # simple OLS
    n    = length(log_x)
    mx   = mean(log_x)
    mE   = mean(log_E)
    γ    = sum((log_x .- mx) .* (log_E .- mE)) / (sum((log_x .- mx).^2) + 1e-10)
    erh_ok = γ <= 0.51
    return (erh_satisfied=erh_ok, estimated_exponent=γ, num_positive=length(pos))
end

# ---------------------------------------------------------------------------
# Simulator state container
# ---------------------------------------------------------------------------

"""
    ABMSimulatorState

Holds the Agents.jl model, per-step history, and the current simulation clock.
"""
mutable struct ABMSimulatorState
    model::StandardABM
    network_topology::String
    simulation_history::Vector{Dict{String,Any}}
    current_time::Int
end

# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

"""
    create_simulator(; num_agents, network_topology, seed) → ABMSimulatorState

Create and initialise an ABM simulator with `num_agents` EthicalAgentABM agents.
Bias strengths are varied across agents to mirror the Python default factory.
"""
function create_simulator(;
    num_agents::Int=100,
    network_topology::String="small_world",
    seed::Int=42
)
    rng   = Xoshiro(seed)
    model = StandardABM(EthicalAgentABM; rng=rng)

    for i in 1:num_agents
        bias  = 0.1 + 0.1 * ((i-1) % 5) / 5.0
        error_rate        = 0.1 + 0.1 * rand(rng)
        judgment_tendency = 0.5 + 0.1 * randn(rng)
        add_agent!(
            model;
            bias_strength=bias,
            error_rate=error_rate,
            judgment_tendency=judgment_tendency,
            num_judgments=0
        )
    end

    ABMSimulatorState(model, network_topology, Dict{String,Any}[], 0)
end

# ---------------------------------------------------------------------------
# Step: evaluate actions with all agents
# ---------------------------------------------------------------------------

"""
    evaluate_step!(sim, actions, τ) → Dict{Int, Vector{Bool}}

Have every agent judge every action.  Updates `error_rate` and `num_judgments`.
Returns a dict agent_id → judgments (Vector{Bool}).
"""
function evaluate_step!(
    sim::ABMSimulatorState,
    actions::Vector{SimAction},
    τ::Float64
)
    results = Dict{Int,Vector{Bool}}()
    for agent in allagents(sim.model)
        judgments = [judge_action(agent, a, τ) for a in actions]
        n_errors  = count(identity, judgments)
        # Update running stats on the mutable agent fields
        agent.num_judgments += length(actions)
        # Exponential moving average for error_rate
        if length(actions) > 0
            step_error = n_errors / length(actions)
            agent.error_rate = 0.9 * agent.error_rate + 0.1 * step_error
        end
        results[agent.id] = judgments
    end
    return results
end

# ---------------------------------------------------------------------------
# Network influence (simplified; full topology in SocialNetwork.jl)
# ---------------------------------------------------------------------------

"""
    scheduled_interactions!(sim, interaction_probability; rng)

Randomly pair agents and let high-error agents be influenced by low-error ones.
This is the lightweight ABM-internal equivalent of the Python `schedule_interactions`.
"""
function scheduled_interactions!(
    sim::ABMSimulatorState,
    interaction_probability::Float64;
    rng::AbstractRNG=Random.default_rng()
)
    agent_list = collect(allagents(sim.model))
    n = length(agent_list)
    n < 2 && return
    for i in 1:n
        if rand(rng) < interaction_probability
            j = rand(rng, 1:n)
            while j == i; j = rand(rng, 1:n); end
            a1, a2 = agent_list[i], agent_list[j]
            # Influence: blend judgment tendencies
            mid = (a1.judgment_tendency + a2.judgment_tendency) / 2
            a1.judgment_tendency = 0.9*a1.judgment_tendency + 0.1*mid
            a2.judgment_tendency = 0.9*a2.judgment_tendency + 0.1*mid
        end
    end
end

# ---------------------------------------------------------------------------
# Main simulation loop
# ---------------------------------------------------------------------------

"""
    run_simulation!(sim; num_time_steps, actions_per_step, τ, X_max,
                    track_erh, interaction_probability, seed) → Dict{String,Any}

Run the ABM for `num_time_steps` steps.

Returns a Dict with keys:
- `"erh_history"`        — per-step ERH metrics
- `"population_history"` — per-step population statistics
- `"final_state"`        — summary after last step
- `"actions_history"`    — the generated action sets (for downstream temporal ERH)
"""
function run_simulation!(
    sim::ABMSimulatorState;
    num_time_steps::Int=10,
    actions_per_step::Int=1000,
    τ::Float64=0.3,
    X_max::Int=100,
    track_erh::Bool=true,
    interaction_probability::Float64=0.1,
    seed::Int=42
)
    erh_history        = Dict{String,Any}[]
    population_history = Dict{String,Any}[]
    actions_history    = Vector{SimAction}[]

    for t in 0:(num_time_steps - 1)
        rng     = Xoshiro(seed + t)
        actions = generate_world(actions_per_step; rng=rng)
        push!(actions_history, actions)

        agent_results = evaluate_step!(sim, actions, τ)

        # --- ERH tracking ---
        if track_erh
            all_primes = SimAction[]
            for (aid, judgments) in agent_results
                p = select_ethical_primes(actions, judgments)
                append!(all_primes, p)
            end

            if !isempty(all_primes)
                Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(all_primes, X_max)
                analysis = analyze_error_growth(E_x, x_vals)
                push!(erh_history, Dict{String,Any}(
                    "time"        => t,
                    "Pi_x"        => Pi_x,
                    "B_x"         => B_x,
                    "E_x"         => E_x,
                    "x_values"    => x_vals,
                    "analysis"    => analysis,
                    "num_primes"  => length(all_primes)
                ))
            else
                push!(erh_history, Dict{String,Any}(
                    "time"       => t,
                    "num_primes" => 0,
                    "analysis"   => (erh_satisfied=false, estimated_exponent=NaN, num_positive=0)
                ))
            end
        end

        # --- Agent interactions ---
        scheduled_interactions!(sim, interaction_probability; rng=rng)

        # --- Population statistics ---
        agents_vec = collect(allagents(sim.model))
        error_rates       = [a.error_rate for a in agents_vec]
        tendencies        = [a.judgment_tendency for a in agents_vec]
        biases            = [a.bias_strength for a in agents_vec]
        push!(population_history, Dict{String,Any}(
            "time"             => t,
            "num_agents"       => length(agents_vec),
            "mean_error_rate"  => mean(error_rates),
            "std_error_rate"   => std(error_rates),
            "mean_tendency"    => mean(tendencies),
            "std_tendency"     => std(tendencies),
            "mean_bias"        => mean(biases)
        ))

        sim.current_time = t
    end

    final_state = Dict{String,Any}(
        "time"             => sim.current_time,
        "population_stats" => isempty(population_history) ? Dict() : last(population_history),
        "network_topology" => sim.network_topology
    )

    push!(sim.simulation_history, Dict{String,Any}(
        "erh_history"        => erh_history,
        "population_history" => population_history,
        "final_state"        => final_state
    ))

    return Dict{String,Any}(
        "erh_history"        => erh_history,
        "population_history" => population_history,
        "final_state"        => final_state,
        "actions_history"    => actions_history
    )
end

# ---------------------------------------------------------------------------
# Temporal ERH from stored actions history
# ---------------------------------------------------------------------------

"""
    compute_temporal_erh(sim, actions_history; τ, X_max) → Dict{String,Any}

Use the first agent as representative judge and compute Π(x,t), B(x,t), E(x,t).
"""
function compute_temporal_erh(
    sim::ABMSimulatorState,
    actions_history::Vector{Vector{SimAction}};
    τ::Float64=0.3,
    X_max::Int=100
)
    T = length(actions_history)
    Pi_xt = zeros(Float64, T, X_max)
    B_xt  = zeros(Float64, T, X_max)

    agents_vec = collect(allagents(sim.model))
    rep_agent  = isempty(agents_vec) ? nothing : first(agents_vec)

    primes_history = Vector{SimAction}[]
    for t in 1:T
        if rep_agent !== nothing
            judgments = [judge_action(rep_agent, a, τ) for a in actions_history[t]]
            primes    = select_ethical_primes(actions_history[t], judgments)
        else
            primes = SimAction[]
        end
        push!(primes_history, primes)
        for x in 1:X_max
            Pi_xt[t, x] = count(p -> p.c <= x, primes)
        end
    end

    # Baseline: β·x/log(x)  (prime-theorem style, matches compute_baseline_temporal)
    beta = 10.0
    for t in 1:T, x in 1:X_max
        B_xt[t, x] = beta * x / max(log(x), 1e-10)
    end

    E_xt = Pi_xt .- B_xt

    # ERH satisfaction rate
    sat_count = 0
    total_pts  = T * X_max
    C, epsilon = 1.0, 0.1
    for t in 1:T, x in 1:X_max
        if abs(E_xt[t, x]) <= C * (x ^ (0.5 + epsilon))
            sat_count += 1
        end
    end
    satisfaction_rate = total_pts > 0 ? sat_count / total_pts : 0.0

    return Dict{String,Any}(
        "Pi_xt"            => Pi_xt,
        "B_xt"             => B_xt,
        "E_xt"             => E_xt,
        "primes_history"   => primes_history,
        "erh_satisfaction" => Dict("satisfaction_rate" => satisfaction_rate,
                                   "violation_rate"    => 1.0 - satisfaction_rate)
    )
end

# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

"""
    calibrate_erh_parameters(simulation_results; target_exponent) → Dict{String,Any}

Analyse ERH history to produce recommendations for parameter adjustment.
"""
function calibrate_erh_parameters(
    simulation_results::Dict{String,Any};
    target_exponent::Float64=0.5
)
    haskey(simulation_results, "erh_history") || return Dict{String,Any}(
        "calibrated" => false, "reason" => "No ERH history available"
    )

    erh_history = simulation_results["erh_history"]
    exponents   = Float64[]
    sat_count   = 0

    for entry in erh_history
        analysis = get(entry, "analysis", nothing)
        analysis === nothing && continue
        exp_val = analysis isa NamedTuple ? analysis.estimated_exponent :
                  get(analysis, "estimated_exponent", NaN)
        isnan(exp_val) || push!(exponents, exp_val)
        sat = analysis isa NamedTuple ? analysis.erh_satisfied :
              get(analysis, "erh_satisfied", false)
        sat && (sat_count += 1)
    end

    mean_exponent    = isempty(exponents) ? NaN : mean(exponents)
    satisfaction_rate = isempty(erh_history) ? 0.0 : sat_count / length(erh_history)

    recommendations = String[]
    if !isnan(mean_exponent)
        if mean_exponent > target_exponent + 0.1
            push!(recommendations, "Reduce bias strength in judges")
            push!(recommendations, "Increase noise filtering")
        elseif mean_exponent < target_exponent - 0.1
            push!(recommendations, "System is performing better than ERH predicts")
        end
    end
    if satisfaction_rate < 0.5
        push!(recommendations, "System frequently violates ERH - consider parameter adjustment")
    end

    return Dict{String,Any}(
        "calibrated"        => true,
        "mean_exponent"     => mean_exponent,
        "target_exponent"   => target_exponent,
        "satisfaction_rate" => satisfaction_rate,
        "recommendations"   => recommendations
    )
end

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

"""
    get_simulation_summary(sim) → Dict{String,Any}
"""
function get_simulation_summary(sim::ABMSimulatorState)
    agents_vec  = collect(allagents(sim.model))
    n           = length(agents_vec)
    error_rates = n > 0 ? [a.error_rate for a in agents_vec] : [0.0]
    tendencies  = n > 0 ? [a.judgment_tendency for a in agents_vec] : [0.0]
    return Dict{String,Any}(
        "current_time"              => sim.current_time,
        "num_agents"                => n,
        "network_topology"          => sim.network_topology,
        "simulation_steps_completed"=> length(sim.simulation_history),
        "mean_error_rate"           => mean(error_rates),
        "mean_tendency"             => mean(tendencies)
    )
end

end # module ABMSimulator
