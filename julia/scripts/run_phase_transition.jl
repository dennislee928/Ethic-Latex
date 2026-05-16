#!/usr/bin/env julia
"""
Phase Transition Experiment: Coupling Strength J vs Ethical Stability (Julia)

Sweeps coupling strength J from J_min to J_max. For each J:
  1. Quantum proxy: exponential decay model (no external quantum backend needed)
  2. Judgement: synthetic action world → BiasedJudge → error_rate

Output: simulation/output/phase_transition_results.json
        figures/phase_transition.png  (with --save-plot)

Usage:
    julia --project=julia julia/scripts/run_phase_transition.jl [options]
    julia --project=julia julia/scripts/run_phase_transition.jl --smoke
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
        "output_dir"  => nothing,
        "J_min"       => 0.0,
        "J_max"       => 2.0,
        "n_points"    => 21,
        "seed"        => 42,
        "n_qubits"    => 4,
        "num_actions" => 100,
        "no_oracle"   => true,   # always true in Julia version (no HuggingFace)
        "save_plot"   => false,
        "smoke"       => false,
    )
    i = 1
    while i <= length(argv)
        a = argv[i]
        if a == "--smoke"
            args["smoke"] = true
        elseif a == "--save-plot"
            args["save_plot"] = true
        elseif a == "--no-oracle"
            args["no_oracle"] = true
        elseif a == "--output-dir" && i < length(argv)
            i += 1; args["output_dir"] = argv[i]
        elseif a == "--J-min" && i < length(argv)
            i += 1; args["J_min"] = parse(Float64, argv[i])
        elseif a == "--J-max" && i < length(argv)
            i += 1; args["J_max"] = parse(Float64, argv[i])
        elseif a == "--n-points" && i < length(argv)
            i += 1; args["n_points"] = parse(Int, argv[i])
        elseif a == "--seed" && i < length(argv)
            i += 1; args["seed"] = parse(Int, argv[i])
        elseif a == "--n-qubits" && i < length(argv)
            i += 1; args["n_qubits"] = parse(Int, argv[i])
        elseif a == "--num-actions" && i < length(argv)
            i += 1; args["num_actions"] = parse(Int, argv[i])
        end
        i += 1
    end
    return args
end

# ---------------------------------------------------------------------------
# Simulation helpers (shared with run_simulation_batch)
# ---------------------------------------------------------------------------
function generate_world(; num_actions::Int, complexity_dist::String="zipf", seed::Int=42)
    rng = MersenneTwister(seed)
    actions = []
    for i in 1:num_actions
        c = if complexity_dist == "zipf"
            clamp(round(Int, 100 / (rand(rng) * 99 + 1)), 1, 100)
        elseif complexity_dist == "uniform"
            rand(rng, 1:100)
        else
            clamp(round(Int, 100 * rand(rng)^2), 1, 100)
        end
        w = rand(rng)
        v = rand(rng)
        push!(actions, (id=i, c=c, w=w, v=v, mistake_flag=false))
    end
    return actions
end

function evaluate_judgement!(actions; bias_strength=0.2, noise_scale=0.1, tau=0.3, seed=0)
    rng = MersenneTwister(seed + 9999)
    result = []
    for a in actions
        judgment = clamp(a.v + bias_strength * (0.5 - a.v) + randn(rng) * noise_scale, 0.0, 1.0)
        push!(result, merge(a, (mistake_flag=(abs(judgment - a.v) > tau),)))
    end
    return result
end

# ---------------------------------------------------------------------------
# Quantum fidelity proxy (no external dependency)
# ---------------------------------------------------------------------------
function quantum_fidelity_proxy(J::Float64, n_qubits::Int, rng::AbstractRNG)
    # Exponential decay: higher J → lower fidelity (phase transition)
    fid = 0.8 * exp(-0.5 * J) + 0.1 * rand(rng)
    return clamp(fid, 0.0, 1.0)
end

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function main()
    args = parse_args()

    if args["smoke"]
        println("[smoke] run_phase_transition: minimal run (3 J points, 10 actions)")
        args["n_points"]    = 3
        args["num_actions"] = 10
        args["save_plot"]   = false
    end

    project_root = joinpath(@__DIR__, "..", "..")
    output_dir   = something(
        args["output_dir"] !== nothing ? args["output_dir"] : nothing,
        joinpath(project_root, "simulation", "output"),
    )
    mkpath(output_dir)
    figures_dir = joinpath(output_dir, "figures")
    mkpath(figures_dir)

    J_min     = args["J_min"]
    J_max     = args["J_max"]
    n_points  = args["n_points"]
    seed      = args["seed"]
    n_qubits  = args["n_qubits"]
    n_actions = args["num_actions"]

    J_values = range(J_min, J_max; length=n_points) |> collect
    rng      = MersenneTwister(seed)

    error_rates = Float64[]
    fidelities  = Float64[]

    println("[phase_transition] Sweeping J over $(n_points) points [$J_min, $J_max]")
    for (k, J) in enumerate(J_values)
        fid = quantum_fidelity_proxy(J, n_qubits, rng)
        push!(fidelities, fid)

        actions = generate_world(
            num_actions=n_actions,
            complexity_dist="zipf",
            seed=seed + round(Int, J * 100),
        )
        actions = evaluate_judgement!(actions; bias_strength=0.2, tau=0.3, seed=seed)
        er = mean(a -> a.mistake_flag ? 1.0 : 0.0, actions)
        push!(error_rates, er)

        if k % max(1, n_points ÷ 5) == 0
            println("  J=$(round(J; digits=3)) | error_rate=$(round(er; digits=4)) | fidelity=$(round(fid; digits=4))")
        end
    end

    stability = 1.0 .- error_rates

    # Critical point: first J where error_rate > 0.5
    idx = findfirst(e -> e > 0.5, error_rates)
    critical_point_J = idx !== nothing ? J_values[idx] : nothing

    result = Dict(
        "coupling_strengths" => J_values,
        "error_rates"        => error_rates,
        "fidelities"         => fidelities,
        "stability"          => stability,
        "critical_point_J"   => critical_point_J,
        "seed"               => seed,
        "n_qubits"           => n_qubits,
        "J_range"            => [J_min, J_max],
        "n_points"           => n_points,
        "use_oracle"         => false,
    )

    out_path = joinpath(output_dir, "phase_transition_results.json")
    open(out_path, "w") do io
        JSON3.pretty(io, result)
    end
    println("[phase_transition] Results saved to $out_path")

    if critical_point_J !== nothing
        println("[phase_transition] Critical point J_c ≈ $(round(critical_point_J; digits=3))")
    else
        println("[phase_transition] No critical point found in J range")
    end

    if args["save_plot"]
        try
            fig = Figure(size=(800, 500))
            ax  = Axis(fig[1, 1];
                xlabel="Coupling Strength J",
                ylabel="Ethical Stability / Fidelity",
                title="Phase Transition: J vs Ethical Stability",
            )
            lines!(ax, J_values, stability;    label="Ethical Stability (1 - Error Rate)", color=:blue)
            lines!(ax, J_values, fidelities;   label="Quantum Fidelity",  linestyle=:dash, color=:orange)
            if critical_point_J !== nothing
                vlines!(ax, [critical_point_J]; color=:red, linestyle=:dash, alpha=0.7, label="J_c")
            end
            axislegend(ax; position=:rt)
            plot_path = joinpath(figures_dir, "phase_transition.png")
            save(plot_path, fig)
            println("[phase_transition] Figure saved to $plot_path")
        catch e
            println("[phase_transition] Could not save plot: $e")
        end
    end
end

main()
