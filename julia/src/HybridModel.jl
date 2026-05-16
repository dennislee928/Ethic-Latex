"""
    HybridModel — Integrated psychohistory model combining all simulation components.

    Mirrors erh_core/core/hybrid_model.py.

    Combines:
    - ABMSimulator      (agent-based simulation)
    - SocialNetwork     (graph structure + opinion dynamics)
    - TemporalERH       (temporal Π/B/E tracking)
    - FluidModel        (PDE-based error density evolution, optional)

    Note: the quantum component (AdvancedEthicalQuantumEngine) is handled by
    QuantumSimulator.jl and is exposed via an optional `enable_quantum` flag
    that is a no-op until Phase 3 files are compiled.
"""
module HybridModel

using Statistics
using LinearAlgebra

# Sibling modules (resolved at ERH module level via include order in ERH.jl)
import ..ABMSimulator as ABMS
import ..SocialNetwork as SN
import ..TemporalERH as TERH
import ..FluidModel as FM

export HybridPsychohistoryModel, create_hybrid_model,
       run_hybrid_simulation!, adaptive_adjustment,
       get_unified_metrics, get_hybrid_summary

# ---------------------------------------------------------------------------
# Config struct
# ---------------------------------------------------------------------------

"""
    HybridConfig

Feature flags and hyperparameters for the hybrid model.
"""
struct HybridConfig
    num_agents::Int
    network_topology::String
    enable_temporal::Bool
    enable_network_dynamics::Bool
    enable_fluid_model::Bool
    enable_meta_monitor::Bool
    enable_quantum::Bool
    network_dynamics_model::String   # "degroot" | "hegselmann_krause"
    seed::Int
end

function HybridConfig(;
    num_agents::Int=100,
    network_topology::String="small_world",
    enable_temporal::Bool=true,
    enable_network_dynamics::Bool=true,
    enable_fluid_model::Bool=false,
    enable_meta_monitor::Bool=true,
    enable_quantum::Bool=false,
    network_dynamics_model::String="degroot",
    seed::Int=42
)
    HybridConfig(num_agents, network_topology, enable_temporal,
                 enable_network_dynamics, enable_fluid_model,
                 enable_meta_monitor, enable_quantum,
                 network_dynamics_model, seed)
end

# ---------------------------------------------------------------------------
# Main model struct
# ---------------------------------------------------------------------------

"""
    HybridPsychohistoryModel

Holds the ABM simulator, the social network (lazily initialised from ABM state),
and runtime configuration.
"""
mutable struct HybridPsychohistoryModel
    config::HybridConfig
    abm::ABMS.ABMSimulatorState
    network::Union{SN.SocialNetworkState, Nothing}
    simulation_state::Dict{String, Any}
end

# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

"""
    create_hybrid_model(; kwargs...) → HybridPsychohistoryModel

Convenience constructor.  All kwargs are forwarded to `HybridConfig`.
"""
function create_hybrid_model(; kwargs...)
    cfg = HybridConfig(; kwargs...)
    abm = ABMS.create_simulator(;
        num_agents       = cfg.num_agents,
        network_topology = cfg.network_topology,
        seed             = cfg.seed
    )

    # Build the social network from initial ABM agent state
    using Agents: allagents
    agents_vec = collect(allagents(abm.model))
    agent_ids  = [a.id for a in agents_vec]
    error_rates = [a.error_rate for a in agents_vec]
    tendencies  = [a.judgment_tendency for a in agents_vec]

    network = SN.create_network(
        agent_ids, error_rates, tendencies;
        topology = cfg.network_topology,
        seed     = cfg.seed
    )

    sim_state = Dict{String,Any}(
        "time"          => 0,
        "erh_history"   => Any[],
        "network_history" => Any[],
        "fluid_history" => Any[]
    )

    HybridPsychohistoryModel(cfg, abm, network, sim_state)
end

# ---------------------------------------------------------------------------
# Main simulation entry point
# ---------------------------------------------------------------------------

"""
    run_hybrid_simulation!(model; num_time_steps, actions_per_step, τ, X_max,
                            fluid_model_params) → Dict{String,Any}

Run a complete hybrid simulation and return a comprehensive results dict.

Keys in the returned dict:
- `"abm_results"`        — raw output from ABMSimulator
- `"temporal_erh"`       — Π/B/E arrays (if `enable_temporal`)
- `"network_dynamics"`   — opinion dynamics result (if `enable_network_dynamics`)
- `"aggregated_beliefs"` — per-agent aggregated errors
- `"fluid_model"`        — PDE solution dict (if `enable_fluid_model`)
"""
function run_hybrid_simulation!(
    model::HybridPsychohistoryModel;
    num_time_steps::Int=10,
    actions_per_step::Int=1000,
    τ::Float64=0.3,
    X_max::Int=100,
    fluid_model_params::Union{Dict{String,Float64}, Nothing}=nothing
)::Dict{String, Any}

    # --- ABM ---
    abm_results = ABMS.run_simulation!(
        model.abm;
        num_time_steps       = num_time_steps,
        actions_per_step     = actions_per_step,
        τ                    = τ,
        X_max                = X_max,
        track_erh            = model.config.enable_temporal,
        interaction_probability = 0.1,
        seed                 = model.config.seed
    )

    results = Dict{String,Any}(
        "abm_results"        => abm_results,
        "temporal_erh"       => nothing,
        "network_dynamics"   => nothing,
        "aggregated_beliefs" => nothing,
        "fluid_model"        => nothing,
        "quantum_stability"  => nothing
    )

    # --- Temporal ERH ---
    if model.config.enable_temporal && haskey(abm_results, "actions_history")
        temporal = ABMS.compute_temporal_erh(
            model.abm,
            abm_results["actions_history"];
            τ    = τ,
            X_max = X_max
        )
        results["temporal_erh"] = temporal
    end

    # --- Network dynamics ---
    if model.config.enable_network_dynamics && model.network !== nothing
        using Agents: allagents
        agents_vec = collect(allagents(model.abm.model))
        tendencies  = [a.judgment_tendency for a in agents_vec]
        agent_ids   = [a.id for a in agents_vec]
        error_rates = [a.error_rate for a in agents_vec]

        # Sync network node attributes
        SN.update_node_attributes!(model.network, agent_ids, error_rates, tendencies)

        dyn_result = if model.config.network_dynamics_model == "degroot"
            SN.degroot_model!(tendencies, model.network)
        else
            SN.hegselmann_krause_model!(tendencies, model.network)
        end
        results["network_dynamics"] = dyn_result

        individual_errors = Dict(agent_ids[i] => error_rates[i] for i in eachindex(agent_ids))
        aggregated = SN.aggregate_beliefs!(
            individual_errors, model.network;
            dynamics_model = model.config.network_dynamics_model
        )
        results["aggregated_beliefs"] = aggregated
    end

    # --- Fluid model ---
    if model.config.enable_fluid_model
        temporal = results["temporal_erh"]
        if temporal !== nothing && haskey(temporal, "E_xt")
            E_xt = temporal["E_xt"]
            T    = size(E_xt, 1)
            x_vals = collect(1.0:Float64(X_max))
            t_vals = collect(0.0:Float64(T-1))

            fitted = FM.fit_fluid_parameters(E_xt, x_vals, t_vals)
            params = fluid_model_params !== nothing ? fluid_model_params : fitted

            try
                nx_fluid = min(50, X_max)
                nt_fluid = min(50, T)
                u_xt, x_grid, t_grid = FM.solve_error_density_pde(
                    (1.0, Float64(X_max)), (0.0, Float64(T));
                    nx = nx_fluid, nt = nt_fluid,
                    v  = get(params, "v",     0.1),
                    D  = get(params, "D",     0.01),
                    alpha = get(params, "alpha", 0.05)
                )
                critical = FM.detect_critical_phenomena(u_xt, x_grid, t_grid)
                results["fluid_model"] = Dict{String,Any}(
                    "u_xt"           => u_xt,
                    "x_grid"         => x_grid,
                    "t_grid"         => t_grid,
                    "parameters"     => params,
                    "critical_events"=> critical
                )
            catch e
                results["fluid_model"] = Dict{String,Any}("error" => string(e))
            end
        end
    end

    # Update state
    model.simulation_state["time"]        = num_time_steps
    model.simulation_state["erh_history"] = get(abm_results, "erh_history", Any[])

    return results
end

# ---------------------------------------------------------------------------
# Adaptive adjustment
# ---------------------------------------------------------------------------

"""
    adaptive_adjustment(model, simulation_results; target_exponent) → Dict{String,Any}

Calibrate ERH parameters and surface recommendations based on simulation output.
"""
function adaptive_adjustment(
    model::HybridPsychohistoryModel,
    simulation_results::Dict{String,Any};
    target_exponent::Float64=0.5
)::Dict{String,Any}
    adjustments = Dict{String,Any}()

    # ABM-level calibration
    if haskey(simulation_results, "abm_results")
        calibration = ABMS.calibrate_erh_parameters(
            simulation_results["abm_results"];
            target_exponent = target_exponent
        )
        adjustments["abm_calibration"] = calibration
    end

    # Temporal ERH parameter scan
    if haskey(simulation_results, "temporal_erh") &&
       simulation_results["temporal_erh"] !== nothing
        terh = simulation_results["temporal_erh"]
        if haskey(terh, "E_xt")
            E_xt = terh["E_xt"]
            T, Xn = size(E_xt)
            # Estimate global exponent from |E_xt| vs x
            x_vals  = Float64.(1:Xn)
            abs_E   = abs.(E_xt)
            mean_E  = vec(mean(abs_E, dims=1))
            pos     = findall(e -> e > 0, mean_E)
            if length(pos) >= 3
                lx = log.(x_vals[pos])
                lE = log.(mean_E[pos])
                mx, mE2 = mean(lx), mean(lE)
                gamma = sum((lx .- mx) .* (lE .- mE2)) /
                        (sum((lx .- mx).^2) + 1e-10)
                adjustments["estimated_global_exponent"] = gamma
                adjustments["erh_parameters"] = Dict(
                    "C"       => 1.0,
                    "epsilon" => max(0.0, gamma - 0.5)
                )
            end
        end
    end

    return adjustments
end

# ---------------------------------------------------------------------------
# Unified metrics
# ---------------------------------------------------------------------------

"""
    get_unified_metrics(simulation_results) → Dict{String,Any}

Compute composite metrics across ABM, temporal ERH, and network dynamics.
"""
function get_unified_metrics(simulation_results::Dict{String,Any})::Dict{String,Any}
    metrics = Dict{String,Any}(
        "erh_satisfaction"   => nothing,
        "temporal_stability" => nothing,
        "network_coherence"  => nothing,
        "system_health"      => nothing
    )

    # ERH satisfaction
    terh = get(simulation_results, "temporal_erh", nothing)
    if terh !== nothing && haskey(terh, "erh_satisfaction")
        sat = terh["erh_satisfaction"]
        metrics["erh_satisfaction"] = Dict(
            "satisfaction_rate" => get(sat, "satisfaction_rate", 0.0),
            "violation_rate"    => get(sat, "violation_rate",    0.0)
        )
    end

    # Temporal stability (volatility of E_xt)
    if terh !== nothing && haskey(terh, "E_xt")
        E_xt = terh["E_xt"]
        abs_E = abs.(E_xt)
        volatility = std(abs_E)
        metrics["temporal_stability"] = Dict(
            "volatility"  => volatility,
            "mean_error"  => mean(abs_E)
        )
    end

    # Network coherence
    net_dyn = get(simulation_results, "network_dynamics", nothing)
    if net_dyn !== nothing
        metrics["network_coherence"] = Dict(
            "converged"  => net_dyn.converged,
            "iterations" => net_dyn.iterations,
            "clusters"   => hasfield(typeof(net_dyn), :clusters) ?
                            length(net_dyn.clusters) : 0
        )
    end

    # System health composite
    health_score = 1.0
    if metrics["erh_satisfaction"] !== nothing
        health_score *= get(metrics["erh_satisfaction"], "satisfaction_rate", 1.0)
    end
    if metrics["temporal_stability"] !== nothing
        vol = get(metrics["temporal_stability"], "volatility", 0.0)
        health_score *= max(0.0, 1.0 - vol / 0.5)
    end
    if metrics["network_coherence"] !== nothing
        health_score *= get(metrics["network_coherence"], "converged", false) ? 1.1 : 0.9
    end

    score  = clamp(health_score, 0.0, 1.0)
    status = score > 0.7 ? "healthy" : score > 0.4 ? "degraded" : "critical"
    metrics["system_health"] = Dict("score" => score, "status" => status)

    return metrics
end

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

"""
    get_hybrid_summary(model) → Dict{String,Any}
"""
function get_hybrid_summary(model::HybridPsychohistoryModel)::Dict{String,Any}
    abm_summary = ABMS.get_simulation_summary(model.abm)
    net_stats   = model.network !== nothing ?
                  SN.get_network_statistics(model.network) :
                  Dict{String,Any}()

    return Dict{String,Any}(
        "num_agents"       => model.config.num_agents,
        "network_topology" => model.config.network_topology,
        "features_enabled" => Dict(
            "temporal"         => model.config.enable_temporal,
            "network_dynamics" => model.config.enable_network_dynamics,
            "fluid_model"      => model.config.enable_fluid_model,
            "meta_monitor"     => model.config.enable_meta_monitor,
            "quantum"          => model.config.enable_quantum
        ),
        "simulation_state" => model.simulation_state,
        "abm_summary"      => abm_summary,
        "network_stats"    => net_stats
    )
end

end # module HybridModel
