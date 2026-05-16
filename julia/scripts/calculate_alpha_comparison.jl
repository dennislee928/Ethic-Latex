#!/usr/bin/env julia
"""
Calculate Real-World α vs Simulated Conservative α and generate comparison plot (Julia).

Mirrors scripts/calculate_alpha_comparison.py.
Output: figures/alpha_comparison_real_vs_simulated.png

NOTE on external data dependencies:
  Real-world α values are read from simulation/output/real_world_results.json if it exists
  (produced by run_empirical_validation.jl / run_empirical_validation.py).
  If the file is absent, only the simulated Conservative α is plotted.

Usage:
    julia --project=julia julia/scripts/calculate_alpha_comparison.jl [options]
    julia --project=julia julia/scripts/calculate_alpha_comparison.jl --smoke
"""

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using ERH
using CairoMakie
using JSON3
using Random
using Statistics

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
function parse_args(argv=ARGS)
    args = Dict{String,Any}(
        "output"      => nothing,
        "results_json"=> nothing,
        "num_seeds"   => 10,
        "smoke"       => false,
    )
    i = 1
    while i <= length(argv)
        a = argv[i]
        if a == "--smoke"
            args["smoke"] = true
        elseif a == "--output" && i < length(argv)
            i += 1; args["output"] = argv[i]
        elseif a == "--results-json" && i < length(argv)
            i += 1; args["results_json"] = argv[i]
        elseif a == "--num-seeds" && i < length(argv)
            i += 1; args["num_seeds"] = parse(Int, argv[i])
        end
        i += 1
    end
    return args
end

# ---------------------------------------------------------------------------
# Simulation helpers
# ---------------------------------------------------------------------------
function generate_world(; num_actions::Int, seed::Int=42)
    rng = MersenneTwister(seed)
    [(id=i,
      c=clamp(round(Int, 100 / (rand(rng)*99 + 1)), 1, 100),
      w=rand(rng),
      v=rand(rng),
      mistake_flag=false) for i in 1:num_actions]
end

function evaluate_conservative!(actions; tau=0.15, seed=300)
    rng = MersenneTwister(seed)
    [merge(a, (mistake_flag=(abs(clamp(a.v + 0.1*(0.5-a.v) + randn(rng)*0.05, 0.0, 1.0) - a.v) > tau),))
     for a in actions]
end

function select_primes(actions; q=0.9)
    thresh = quantile([a.w for a in actions], q)
    filter(a -> a.w >= thresh, actions)
end

function fit_alpha(primes; X_max=100)
    E_x = begin
        Pi_x = [count(p -> p.c <= x, primes) for x in 1:X_max]
        B_x  = [x <= 1 ? 1.0 : x/log(x)     for x in 1:X_max]
        Pi_x .- B_x
    end
    valid = [(log(x), log(abs(e) + 1e-9)) for (x, e) in zip(1:X_max, E_x) if x > 1 && abs(e) > 1e-9]
    length(valid) < 5 && return 0.5
    lx = [v[1] for v in valid]
    ly = [v[2] for v in valid]
    mx, my = mean(lx), mean(ly)
    sum((lx .- mx) .* (ly .- my)) / (sum((lx .- mx).^2) + 1e-12)
end

function get_simulated_conservative_alpha(; num_seeds=10)
    alphas = Float64[]
    for seed in 0:(num_seeds - 1)
        actions = generate_world(num_actions=1000, seed=seed)
        acts    = evaluate_conservative!(actions; tau=0.15, seed=seed+300)
        primes  = select_primes(acts; q=0.9)
        push!(alphas, fit_alpha(primes))
    end
    isempty(alphas) ? 0.5 : mean(alphas)
end

# ---------------------------------------------------------------------------
# Load real-world alpha values from cached JSON
# ---------------------------------------------------------------------------
function get_real_world_alphas(json_path::String)
    result = Dict{String, Float64}()
    isfile(json_path) || return result
    try
        data = JSON3.read(read(json_path, String))
        for (dataset, key) in [("COMPAS", "compas"), ("Adult Income", "adult")]
            d = get(data, Symbol(key), nothing)
            d === nothing && continue
            alpha = get(d, :alpha, nothing)
            alpha !== nothing && (result[dataset] = Float64(alpha))
        end
    catch e
        println("[alpha_comparison] Could not read $json_path: $e")
    end
    return result
end

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
function generate_plot(real_alphas, simulated_alpha, output_path)
    labels = String[]
    values = Float64[]
    colors = Symbol[]

    for (name, alpha) in sort(collect(real_alphas); by=first)
        push!(labels, "Real: $name")
        push!(values, alpha)
        push!(colors, :mediumseagreen)
    end
    push!(labels, "Simulated: Conservative")
    push!(values, simulated_alpha)
    push!(colors, :steelblue)

    n   = length(labels)
    fig = Figure(size=(800, 500))
    ax  = Axis(fig[1,1];
        xlabel  = "Dataset / Judge",
        ylabel  = "Growth exponent α",
        title   = "Real World α vs Simulated Conservative α (ERH)",
        xticks  = (1:n, labels),
        xticklabelrotation = 0.3,
    )
    barplot!(ax, 1:n, values; color=[string(c) for c in colors])
    hlines!(ax, [0.0]; color=:gray, linewidth=0.5)

    # Value labels on bars
    for (j, v) in enumerate(values)
        text!(ax, j, v + 0.02; text="$(round(v; digits=3))",
              align=(:center, :bottom), fontsize=10)
    end

    mkpath(dirname(output_path))
    save(output_path, fig; px_per_unit=150/96)
    println("[alpha_comparison] Plot saved to $output_path")
end

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function main()
    args = parse_args()

    if args["smoke"]
        println("[smoke] calculate_alpha_comparison: 2 seeds, no plot output")
        args["num_seeds"] = 2
    end

    project_root  = joinpath(@__DIR__, "..", "..")
    default_out   = joinpath(project_root, "figures", "alpha_comparison_real_vs_simulated.png")
    output_path   = args["output"] !== nothing ? args["output"] : default_out

    default_json  = joinpath(project_root, "simulation", "output", "real_world_results.json")
    results_json  = args["results_json"] !== nothing ? args["results_json"] : default_json

    println("[alpha_comparison] Loading real-world alphas from $results_json ...")
    real_alphas = get_real_world_alphas(results_json)
    isempty(real_alphas) && println("[alpha_comparison] No real-world data found; plot will show simulated only.")

    println("[alpha_comparison] Computing simulated Conservative α ($(args["num_seeds"]) seeds)...")
    simulated_alpha = get_simulated_conservative_alpha(num_seeds=args["num_seeds"])
    println("[alpha_comparison] Simulated Conservative α = $(round(simulated_alpha; digits=4))")

    if !args["smoke"]
        generate_plot(real_alphas, simulated_alpha, output_path)
    else
        println("[smoke] Skipping plot generation in smoke mode")
    end
end

main()
