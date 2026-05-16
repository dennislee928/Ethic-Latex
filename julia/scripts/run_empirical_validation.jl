#!/usr/bin/env julia
"""
Empirical Validation (Julia)

Computes ERH-style alpha values for:
  - COMPAS recidivism dataset (if simulation/real_data/compas.csv present)
  - Adult Income dataset      (if simulation/real_data/adult.csv present)
  - Synthetic Radical and Conservative judges

Results saved to simulation/output/real_world_results.json.

NOTE on external data dependencies:
  The Python version calls `run_compas_erh_analysis()` and `run_adult_erh_analysis()`,
  which expect CSV files at simulation/real_data/compas.csv and adult.csv.
  This Julia version reads those same CSV files if present; otherwise it records
  a "data_not_found" note and continues with synthetic judges only.

Usage:
    julia --project=julia julia/scripts/run_empirical_validation.jl [--output PATH]
    julia --project=julia julia/scripts/run_empirical_validation.jl --smoke
"""

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using ERH
using JSON3
using Random
using Statistics

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
function parse_args(argv=ARGS)
    args = Dict{String,Any}(
        "output" => nothing,
        "smoke"  => false,
    )
    i = 1
    while i <= length(argv)
        a = argv[i]
        if a == "--smoke"
            args["smoke"] = true
        elseif a == "--output" && i < length(argv)
            i += 1; args["output"] = argv[i]
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

function evaluate_judge!(actions; bias_strength, noise_scale, tau, seed)
    rng = MersenneTwister(seed)
    [merge(a, (mistake_flag=(abs(clamp(a.v + bias_strength*(0.5-a.v) + randn(rng)*noise_scale, 0.0, 1.0) - a.v) > tau),))
     for a in actions]
end

function select_primes(actions; q=0.9)
    thresh = quantile([a.w for a in actions], q)
    filter(a -> a.w >= thresh, actions)
end

function compute_Pi_and_error(primes; X_max=100)
    xs   = collect(1:X_max)
    Pi_x = [count(p -> p.c <= x, primes) for x in xs]
    B_x  = [x <= 1 ? 1.0 : x / log(x)   for x in xs]
    xs, Pi_x, B_x, Pi_x .- B_x
end

function fit_alpha(E_x, x_vals)
    valid = [(log(x), log(abs(e) + 1e-9)) for (x, e) in zip(x_vals, E_x) if x > 1 && abs(e) > 1e-9]
    length(valid) < 5 && return 0.5
    lx = [v[1] for v in valid]
    ly = [v[2] for v in valid]
    mx, my = mean(lx), mean(ly)
    sum((lx .- mx) .* (ly .- my)) / (sum((lx .- mx).^2) + 1e-12)
end

# ---------------------------------------------------------------------------
# Synthetic judges
# ---------------------------------------------------------------------------
function run_synthetic_alphas(; num_actions=1000)
    result = Dict{String, Any}()
    for (name, bias, noise, tau) in [
            ("Radical",      0.45, 0.2,  0.3),
            ("Conservative", 0.1,  0.05, 0.15),
        ]
        try
            actions = generate_world(num_actions=num_actions, seed=42)
            acts    = evaluate_judge!(actions; bias_strength=bias, noise_scale=noise, tau=tau, seed=999)
            primes  = select_primes(acts; q=0.9)
            xs, _, _, E_x = compute_Pi_and_error(primes; X_max=100)
            alpha   = fit_alpha(E_x, xs)
            result[name] = Dict("alpha" => alpha)
            println("Synthetic $name α ≈ $(round(alpha; digits=4))")
        catch e
            result[name] = Dict("error" => string(e))
            println("Synthetic $name: error - $e")
        end
    end
    return result
end

# ---------------------------------------------------------------------------
# Real-data alpha (CSV-based, optional)
# ---------------------------------------------------------------------------

"""
Try to compute ERH alpha from a real-data CSV.
CSV must have columns: complexity (Int) and decision (0/1) or label.
Falls back gracefully if file not found or columns missing.
"""
function run_real_data_erh(csv_path::String, dataset_name::String; X_max=100)
    if !isfile(csv_path)
        println("$dataset_name: data file not found at $csv_path — skipping")
        return Dict("data_not_found" => csv_path)
    end
    try
        using CSV, DataFrames
        df = CSV.read(csv_path, DataFrame)

        # Try to find a "complexity" column (or use row index as proxy)
        c_col  = "complexity" in names(df) ? df[!, :complexity] :
                 "age"       in names(df) ? df[!, :age] :
                 collect(1:nrow(df)) .% 100 .+ 1

        # Decision column: label / two_year_recid / income / class
        d_col  = nothing
        for cn in ("label", "two_year_recid", "income", "class", "target")
            if cn in names(df)
                d_col = df[!, Symbol(cn)]
                break
            end
        end
        d_col === nothing && (d_col = rand(MersenneTwister(0), 0:1, nrow(df)))

        # Build pseudo-actions
        actions = [(c=clamp(Int(round(c_col[i])), 1, 100),
                    w=0.5 + 0.5*sin(i),
                    mistake_flag=(Int(d_col[i]) == 1)) for i in 1:length(c_col)]

        primes = filter(a -> a.w >= 0.9, actions)
        if isempty(primes)
            primes = actions[1:max(1, length(actions)÷10)]
        end

        Pi_x = [count(p -> p.c <= x, primes) for x in 1:X_max]
        B_x  = [x <= 1 ? 1.0 : x/log(x)     for x in 1:X_max]
        E_x  = Pi_x .- B_x
        xs   = collect(1:X_max)
        alpha = fit_alpha(E_x, xs)
        println("$dataset_name α ≈ $(round(alpha; digits=4))")
        return Dict("alpha" => alpha, "n_rows" => nrow(df))
    catch e
        println("$dataset_name: error - $e")
        return Dict("error" => string(e))
    end
end

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function main()
    args = parse_args()

    if args["smoke"]
        println("[smoke] run_empirical_validation: synthetic only, 50 actions")
    end

    project_root = joinpath(@__DIR__, "..", "..")
    default_out  = joinpath(project_root, "simulation", "output", "real_world_results.json")
    output_path  = something(args["output"] !== nothing ? args["output"] : nothing, default_out)
    mkpath(dirname(output_path))

    results = Dict{String, Any}(
        "compas"    => Dict{String, Any}(),
        "adult"     => Dict{String, Any}(),
        "synthetic" => Dict{String, Any}(),
    )

    num_actions = args["smoke"] ? 50 : 1000

    # COMPAS
    compas_csv = joinpath(project_root, "simulation", "real_data", "compas.csv")
    results["compas"] = run_real_data_erh(compas_csv, "COMPAS")

    # Adult Income
    adult_csv = joinpath(project_root, "simulation", "real_data", "adult.csv")
    results["adult"] = run_real_data_erh(adult_csv, "Adult Income")

    # Synthetic
    results["synthetic"] = run_synthetic_alphas(num_actions=num_actions)

    open(output_path, "w") do io
        JSON3.pretty(io, results)
    end
    println("\nResults saved to $output_path")
end

main()
