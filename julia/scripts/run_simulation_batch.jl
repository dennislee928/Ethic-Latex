#!/usr/bin/env julia
"""
Batch Simulation Runner (Julia)
Execute ERH simulations with configurable parameters and save results to JSON/CSV.
Modes: judge (default) = judge-based ERH analysis; abm = Agent-Based Model simulation.

Usage:
    julia --project=julia julia/scripts/run_simulation_batch.jl [options]
    julia --project=julia julia/scripts/run_simulation_batch.jl --smoke
"""

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using ERH
using JSON3
using Random
using Dates
using Statistics

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
function parse_args(argv=ARGS)
    args = Dict{String,Any}(
        "mode"            => "judge",
        "num_actions"     => 1000,
        "agents"          => 50,
        "steps"           => 100,
        "trials"          => 4,
        "complexity_dist" => "zipf",
        "seed"            => 42,
        "output_dir"      => "results",
        "output"          => nothing,
        "instances"       => 1,
        "configs"         => nothing,
        "smoke"           => false,
    )
    i = 1
    while i <= length(argv)
        a = argv[i]
        if a == "--smoke"
            args["smoke"] = true
        elseif a == "--mode" && i < length(argv)
            i += 1; args["mode"] = argv[i]
        elseif a == "--num-actions" && i < length(argv)
            i += 1; args["num_actions"] = parse(Int, argv[i])
        elseif a == "--agents" && i < length(argv)
            i += 1; args["agents"] = parse(Int, argv[i])
        elseif a == "--steps" && i < length(argv)
            i += 1; args["steps"] = parse(Int, argv[i])
        elseif a == "--trials" && i < length(argv)
            i += 1; args["trials"] = parse(Int, argv[i])
        elseif a == "--complexity-dist" && i < length(argv)
            i += 1; args["complexity_dist"] = argv[i]
        elseif a == "--seed" && i < length(argv)
            i += 1; args["seed"] = parse(Int, argv[i])
        elseif a == "--output-dir" && i < length(argv)
            i += 1; args["output_dir"] = argv[i]
        elseif a == "--output" && i < length(argv)
            i += 1; args["output"] = argv[i]
        elseif a == "--instances" && i < length(argv)
            i += 1; args["instances"] = parse(Int, argv[i])
        elseif a == "--configs" && i < length(argv)
            i += 1; args["configs"] = argv[i]
        end
        i += 1
    end
    return args
end

# ---------------------------------------------------------------------------
# ERH simulation helpers (pure-Julia reimplementation)
# ---------------------------------------------------------------------------

"""Generate a synthetic action world with the given complexity distribution."""
function generate_world(; num_actions::Int, complexity_dist::String="zipf", seed::Int=42)
    rng = MersenneTwister(seed)
    actions = []
    for i in 1:num_actions
        c = if complexity_dist == "zipf"
            clamp(round(Int, 100 / (rand(rng) * 99 + 1)), 1, 100)
        elseif complexity_dist == "uniform"
            rand(rng, 1:100)
        else  # power_law
            clamp(round(Int, 100 * rand(rng)^2), 1, 100)
        end
        w = rand(rng)          # moral weight in [0,1]
        v = rand(rng)          # ground-truth value
        push!(actions, (id=i, c=c, w=w, v=v, mistake_flag=false))
    end
    return actions
end

"""Apply biased judge evaluation, setting mistake_flag on each action."""
function evaluate_judgement!(actions; bias_strength=0.2, noise_scale=0.1, tau=0.3, seed=0)
    rng = MersenneTwister(seed + 1000)
    result = []
    for a in actions
        noise = randn(rng) * noise_scale
        judgment = clamp(a.v + bias_strength * (0.5 - a.v) + noise, 0.0, 1.0)
        mistake = abs(judgment - a.v) > tau
        push!(result, merge(a, (mistake_flag=mistake,)))
    end
    return result
end

"""Select ethical primes: top importance_quantile by moral weight."""
function select_ethical_primes(actions; importance_quantile=0.9)
    threshold = quantile([a.w for a in actions], importance_quantile)
    return filter(a -> a.w >= threshold, actions)
end

"""Compute Pi(x), B(x), E(x) and x_vals over [1, X_max]."""
function compute_Pi_and_error(primes; X_max=100)
    x_vals = collect(1:X_max)
    Pi_x = [count(p -> p.c <= x, primes) for x in x_vals]
    # Li(x) approximation as baseline B(x)
    B_x = [x <= 1 ? 1.0 : x / log(x) for x in x_vals]
    E_x = [Pi_x[i] - B_x[i] for i in eachindex(x_vals)]
    return Pi_x, B_x, E_x, x_vals
end

"""Estimate alpha (growth exponent) from |E(x)| in log-log space."""
function analyze_error_growth(E_x, x_vals)
    valid = [(log(x), log(abs(e) + 1e-9)) for (x, e) in zip(x_vals, E_x) if x > 1 && abs(e) > 1e-9]
    if length(valid) < 5
        return Dict("erh_satisfied" => false, "estimated_exponent" => 0.5)
    end
    xs = [v[1] for v in valid]
    ys = [v[2] for v in valid]
    n = length(xs)
    x_mean, y_mean = mean(xs), mean(ys)
    alpha = sum((xs .- x_mean) .* (ys .- y_mean)) / (sum((xs .- x_mean).^2) + 1e-12)
    erh_satisfied = 0.4 <= alpha <= 0.65
    return Dict("erh_satisfied" => erh_satisfied, "estimated_exponent" => alpha)
end

# ---------------------------------------------------------------------------
# ABM simulation helper
# ---------------------------------------------------------------------------
function run_abm_trial(trial_id::Int, n_agents::Int, n_steps::Int, seed::Int)
    rng = MersenneTwister(seed + trial_id * 37)
    # Simple ABM: agents interact, ethical drift accumulates
    state = rand(rng, n_agents)
    erh_history = []
    for t in 1:n_steps
        # Pairwise interactions
        for _ in 1:n_agents
            i, j = rand(rng, 1:n_agents, 2)
            state[i] = clamp(state[i] + 0.01 * (state[j] - state[i]) + 0.01 * randn(rng), 0, 1)
        end
        err = mean(abs.(state .- 0.5))
        push!(erh_history, Dict("t" => t, "mean_error" => err))
    end
    final_error = isempty(erh_history) ? 0.0 : erh_history[end]["mean_error"]
    evs = max(0.0, 1.0 - final_error)
    return Dict(
        "id"               => trial_id,
        "final_error"      => final_error,
        "social_tension"   => 0.0,
        "evs"              => evs,
        "erh_history_len"  => length(erh_history),
    )
end

# ---------------------------------------------------------------------------
# Single simulation run
# ---------------------------------------------------------------------------
function run_single_simulation(sim_id::Int, num_actions::Int, complexity_dist::String, seed::Int)
    t0 = time()
    actions = generate_world(num_actions=num_actions, complexity_dist=complexity_dist, seed=seed)
    actions = evaluate_judgement!(actions; bias_strength=0.2, noise_scale=0.1, tau=0.3, seed=seed)
    primes  = select_ethical_primes(actions; importance_quantile=0.9)
    Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes; X_max=100)
    analysis = analyze_error_growth(E_x, x_vals)
    duration = time() - t0
    mistakes = count(a -> a.mistake_flag, actions)
    return Dict(
        "timestamp" => string(now()),
        "config"    => Dict(
            "id"              => sim_id,
            "num_actions"     => num_actions,
            "complexity_dist" => complexity_dist,
            "seed"            => seed,
        ),
        "metrics"   => Dict(
            "duration_seconds"      => duration,
            "total_actions"         => length(actions),
            "mistakes_count"        => mistakes,
            "mistake_rate"          => mistakes / length(actions),
            "ethical_primes_count"  => length(primes),
            "erh_satisfied"         => get(analysis, "erh_satisfied", false),
            "estimated_exponent"    => get(analysis, "estimated_exponent", nothing),
        ),
    )
end

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function main()
    args = parse_args()

    if args["smoke"]
        println("[smoke] run_simulation_batch: minimal run (2 actions, 1 instance)")
        args["num_actions"] = 2
        args["instances"]   = 1
        args["trials"]      = 1
        args["steps"]       = 2
        args["agents"]      = 2
    end

    mode       = args["mode"]
    output_dir = args["output_dir"]
    mkpath(output_dir)

    if mode == "abm"
        n_agents = args["agents"]
        n_steps  = args["steps"]
        n_trials = args["trials"]
        seed     = args["seed"]
        println("[batch] ABM mode: agents=$n_agents, steps=$n_steps, trials=$n_trials")
        t0 = time()
        results = [run_abm_trial(i, n_agents, n_steps, seed) for i in 0:(n_trials - 1)]
        duration = time() - t0
        output_path = something(args["output"], joinpath(output_dir, "batch_results.json"))
        mkpath(dirname(output_path))
        open(output_path, "w") do io
            JSON3.pretty(io, Dict(
                "config"           => Dict("n_agents" => n_agents, "steps" => n_steps),
                "results"          => results,
                "duration_seconds" => duration,
            ))
        end
        println("[batch] ABM batch completed in $(round(duration; digits=2))s ($n_trials trials) -> $output_path")
        return
    end

    # Judge mode
    configs = if args["configs"] !== nothing && isfile(args["configs"])
        raw = JSON3.read(read(args["configs"], String))
        isa(raw, AbstractArray) ? collect(raw) : [raw]
    else
        n = args["instances"]
        [Dict(
            "id"              => i,
            "num_actions"     => args["num_actions"],
            "complexity_dist" => args["complexity_dist"],
            "seed"            => args["seed"] + i,
        ) for i in 0:(n - 1)]
    end

    println("[batch] Judge mode: $(length(configs)) simulation(s)")
    t0 = time()
    for cfg in configs
        sim_id    = get(cfg, "id", 0)
        n_actions = get(cfg, "num_actions", args["num_actions"])
        cdist     = get(cfg, "complexity_dist", args["complexity_dist"])
        s         = get(cfg, "seed", args["seed"])
        println("  [sim $sim_id] N=$n_actions dist=$cdist seed=$s ...")
        result = run_single_simulation(sim_id, n_actions, cdist, s)
        out_path = joinpath(output_dir, "sim_$(sim_id)_$(Dates.format(now(), "yyyymmdd_HHMMSS")).json")
        open(out_path, "w") do io
            JSON3.pretty(io, result)
        end
        mistakes  = result["metrics"]["mistakes_count"]
        total     = result["metrics"]["total_actions"]
        stability = 1.0 - mistakes / max(total, 1)
        println("  [sim $sim_id] Stability: $(round(stability; digits=3)) -> $out_path")
    end
    elapsed = time() - t0
    println("[batch] Batch completed in $(round(elapsed; digits=2))s ($(length(configs)) simulations)")
end

main()
