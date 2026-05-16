"""
    server.jl — Minimal HTTP microservice for the ERH Julia sidecar.

    Exposes two endpoints:

      GET  /health
          Returns {"status":"ok","version":"0.1.0"}

      POST /simulate
          Accepts JSON body with simulation parameters and runs the requested
          simulation mode, returning JSON results.

    Intended to be called from a Python FastAPI service via HTTP.

    Usage:
        julia --project=. src/server.jl             # default port 8080
        julia --project=. src/server.jl 9000         # custom port

    Environment variables:
        ERH_PORT   override listen port (default 8080)

    JSON body for POST /simulate
    ─────────────────────────────
    {
      "mode":               "abm" | "temporal" | "fluid" | "hybrid",  // default "abm"
      "num_agents":         100,
      "num_time_steps":     10,
      "actions_per_step":   1000,
      "tau":                0.3,
      "X_max":              100,
      "network_topology":   "small_world",
      "interaction_probability": 0.1,
      "enable_temporal":    true,
      "enable_network_dynamics": true,
      "enable_fluid_model": false,
      "seed":               42
    }

    All fields are optional; defaults mirror the Python implementation.
"""

# ---------------------------------------------------------------------------
# Load path: allow running as a standalone script from the julia/ directory.
# ---------------------------------------------------------------------------
using Pkg
Pkg.activate(joinpath(@__DIR__, ".."))   # julia/Project.toml

using HTTP
using JSON3
using Logging

# Bring sibling modules into scope via the ERH package
include(joinpath(@__DIR__, "ABMSimulator.jl"))
include(joinpath(@__DIR__, "SocialNetwork.jl"))
include(joinpath(@__DIR__, "TemporalERH.jl"))
include(joinpath(@__DIR__, "FluidModel.jl"))

import .ABMSimulator as ABMS
import .SocialNetwork as SN
import .TemporalERH as TERH
import .FluidModel as FM

const VERSION_STR = "0.1.0"

# ---------------------------------------------------------------------------
# Helper: safely pull a value from a JSON3 object
# ---------------------------------------------------------------------------

_get(body, key::String, default) = haskey(body, Symbol(key)) ? body[Symbol(key)] : default

# ---------------------------------------------------------------------------
# Serialisation helper
# Converts nested NamedTuples / Matrices to plain Dict/Array for JSON3
# ---------------------------------------------------------------------------

function _serialise(x::Matrix)
    [collect(row) for row in eachrow(x)]
end

_serialise(x::NamedTuple) = Dict(string(k) => _serialise(v) for (k, v) in pairs(x))
_serialise(x::Dict)       = Dict(string(k) => _serialise(v) for (k, v) in pairs(x))
_serialise(x::Vector)     = [_serialise(v) for v in x]
_serialise(x::Nothing)    = nothing
_serialise(x)             = x    # scalars, strings, bools pass through

# ---------------------------------------------------------------------------
# POST /simulate handler
# ---------------------------------------------------------------------------

function handle_simulate(req::HTTP.Request)::HTTP.Response
    body = try
        JSON3.read(req.body)
    catch e
        return HTTP.Response(400, ["Content-Type" => "application/json"],
                             body=JSON3.write(Dict("error" => "Invalid JSON: $(e)")))
    end

    mode                   = String(_get(body, "mode", "abm"))
    num_agents             = Int(_get(body, "num_agents", 100))
    num_time_steps         = Int(_get(body, "num_time_steps", 10))
    actions_per_step       = Int(_get(body, "actions_per_step", 1000))
    tau                    = Float64(_get(body, "tau", 0.3))
    X_max                  = Int(_get(body, "X_max", 100))
    network_topology       = String(_get(body, "network_topology", "small_world"))
    interaction_probability= Float64(_get(body, "interaction_probability", 0.1))
    enable_temporal        = Bool(_get(body, "enable_temporal", true))
    enable_network_dynamics= Bool(_get(body, "enable_network_dynamics", true))
    enable_fluid_model     = Bool(_get(body, "enable_fluid_model", false))
    seed                   = Int(_get(body, "seed", 42))

    result = try
        if mode == "abm"
            # ── ABM-only simulation ──────────────────────────────────────
            sim = ABMS.create_simulator(;
                num_agents       = num_agents,
                network_topology = network_topology,
                seed             = seed
            )
            raw = ABMS.run_simulation!(sim;
                num_time_steps        = num_time_steps,
                actions_per_step      = actions_per_step,
                τ                     = tau,
                X_max                 = X_max,
                track_erh             = enable_temporal,
                interaction_probability = interaction_probability,
                seed                  = seed
            )
            summary = ABMS.get_simulation_summary(sim)
            # Strip the raw actions_history (too large to serialise)
            raw_clean = Dict(k => v for (k, v) in raw if k != "actions_history")
            Dict("status" => "ok", "mode" => "abm",
                 "result" => raw_clean, "summary" => summary)

        elseif mode == "temporal"
            # ── ABM + temporal ERH ───────────────────────────────────────
            sim = ABMS.create_simulator(;
                num_agents       = num_agents,
                network_topology = network_topology,
                seed             = seed
            )
            raw = ABMS.run_simulation!(sim;
                num_time_steps        = num_time_steps,
                actions_per_step      = actions_per_step,
                τ                     = tau,
                X_max                 = X_max,
                track_erh             = true,
                interaction_probability = interaction_probability,
                seed                  = seed
            )
            terh = ABMS.compute_temporal_erh(
                sim, raw["actions_history"]; τ=tau, X_max=X_max
            )
            Dict("status" => "ok", "mode" => "temporal",
                 "erh_satisfaction" => terh["erh_satisfaction"],
                 "Pi_xt_shape"      => size(terh["Pi_xt"]),
                 "E_xt_shape"       => size(terh["E_xt"]))

        elseif mode == "fluid"
            # ── Fluid PDE only ───────────────────────────────────────────
            nx_f = min(50, X_max)
            nt_f = min(50, num_time_steps * 5)
            u_xt, x_grid, t_grid = FM.solve_error_density_pde(
                (1.0, Float64(X_max)), (0.0, Float64(num_time_steps));
                nx=nx_f, nt=nt_f,
                v=Float64(_get(body, "v", 0.1)),
                D=Float64(_get(body, "D", 0.01)),
                alpha=Float64(_get(body, "alpha", 0.05))
            )
            events = FM.detect_critical_phenomena(u_xt, x_grid, t_grid)
            Dict("status"           => "ok",
                 "mode"             => "fluid",
                 "u_xt_shape"       => collect(size(u_xt)),
                 "x_grid"           => x_grid,
                 "t_grid"           => collect(t_grid),
                 "critical_events"  => events,
                 "mean_density"     => sum(u_xt) / length(u_xt))

        elseif mode == "hybrid"
            # ── Full hybrid simulation ───────────────────────────────────
            sim = ABMS.create_simulator(;
                num_agents       = num_agents,
                network_topology = network_topology,
                seed             = seed
            )
            abm_raw = ABMS.run_simulation!(sim;
                num_time_steps        = num_time_steps,
                actions_per_step      = actions_per_step,
                τ                     = tau,
                X_max                 = X_max,
                track_erh             = enable_temporal,
                interaction_probability = interaction_probability,
                seed                  = seed
            )

            # Social network + opinion dynamics
            using Agents: allagents
            agents_vec  = collect(allagents(sim.model))
            agent_ids   = [a.id  for a in agents_vec]
            error_rates = [a.error_rate for a in agents_vec]
            tendencies  = [a.judgment_tendency for a in agents_vec]

            net = SN.create_network(agent_ids, error_rates, tendencies;
                                    topology=network_topology, seed=seed)
            net_stats  = SN.get_network_statistics(net)
            dyn_result = SN.degroot_model!(tendencies, net)

            # Temporal ERH
            terh = nothing
            if enable_temporal && haskey(abm_raw, "actions_history")
                terh = ABMS.compute_temporal_erh(
                    sim, abm_raw["actions_history"]; τ=tau, X_max=X_max
                )
            end

            # Calibration
            calibration = ABMS.calibrate_erh_parameters(abm_raw)

            abm_summary = ABMS.get_simulation_summary(sim)

            Dict("status"        => "ok",
                 "mode"          => "hybrid",
                 "abm_summary"   => abm_summary,
                 "network_stats" => net_stats,
                 "network_dynamics" => Dict(
                     "converged"       => dyn_result.converged,
                     "iterations"      => dyn_result.iterations,
                     "final_opinions"  => dyn_result.final_opinions
                 ),
                 "erh_satisfaction" => terh !== nothing ?
                                       terh["erh_satisfaction"] : nothing,
                 "calibration"      => calibration)
        else
            Dict("error" => "Unknown mode: $mode. Use 'abm', 'temporal', 'fluid', or 'hybrid'.")
        end
    catch e
        @error "Simulation error" exception=(e, catch_backtrace())
        return HTTP.Response(500, ["Content-Type" => "application/json"],
                             body=JSON3.write(Dict("error" => string(e))))
    end

    return HTTP.Response(200, ["Content-Type" => "application/json"],
                         body=JSON3.write(_serialise(result)))
end

# ---------------------------------------------------------------------------
# GET /health handler
# ---------------------------------------------------------------------------

function handle_health(::HTTP.Request)::HTTP.Response
    payload = Dict("status" => "ok", "version" => VERSION_STR,
                   "julia_version" => string(VERSION))
    return HTTP.Response(200, ["Content-Type" => "application/json"],
                         body=JSON3.write(payload))
end

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

function route(req::HTTP.Request)::HTTP.Response
    if req.target == "/health" && req.method == "GET"
        return handle_health(req)
    elseif req.target == "/simulate" && req.method == "POST"
        return handle_simulate(req)
    else
        return HTTP.Response(404, ["Content-Type" => "application/json"],
                             body=JSON3.write(Dict("error" => "Not found: $(req.method) $(req.target)")))
    end
end

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

const DEFAULT_PORT = 8080

function main()
    port_str = get(ENV, "ERH_PORT", length(ARGS) > 0 ? ARGS[1] : string(DEFAULT_PORT))
    port     = parse(Int, port_str)
    @info "ERH Julia sidecar starting" port=port version=VERSION_STR
    HTTP.serve(route, "0.0.0.0", port; verbose=false)
end

# Run when executed as a script (not when included by tests)
if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
