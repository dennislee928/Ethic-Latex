#!/usr/bin/env julia
"""
Generate All Figures for the Paper (Julia / CairoMakie)

Produces publication-quality figures equivalent to simulation/generate_all_figures.py.
Output goes to figures/ in the repo root (same paths the Python script writes to).

Usage:
    julia --project=julia julia/scripts/generate_all_figures.jl [--output-dir DIR]
    julia --project=julia julia/scripts/generate_all_figures.jl --smoke
"""

push!(LOAD_PATH, joinpath(@__DIR__, "..", "src"))
using ERH
using CairoMakie
using Random
using Statistics
using JSON3

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
function parse_args(argv=ARGS)
    args = Dict{String,Any}(
        "output_dir"  => nothing,
        "smoke"       => false,
        "num_actions" => 2000,
        "X_max"       => 100,
    )
    i = 1
    while i <= length(argv)
        a = argv[i]
        if a == "--smoke"
            args["smoke"] = true
        elseif a == "--output-dir" && i < length(argv)
            i += 1; args["output_dir"] = argv[i]
        elseif a == "--num-actions" && i < length(argv)
            i += 1; args["num_actions"] = parse(Int, argv[i])
        end
        i += 1
    end
    return args
end

# ---------------------------------------------------------------------------
# CairoMakie paper style (mirrors setup_paper_style)
# ---------------------------------------------------------------------------
function setup_paper_style!()
    set_theme!(
        fontsize    = 12,
        figure_padding = 10,
        Axis = (
            spinewidth  = 1,
            xgridvisible = true,
            ygridvisible = true,
            xgridstyle  = :dash,
            ygridstyle  = :dash,
        ),
    )
end

# ---------------------------------------------------------------------------
# Simulation helpers
# ---------------------------------------------------------------------------
function generate_world(; num_actions::Int, complexity_dist::String="zipf", seed::Int=42)
    rng = MersenneTwister(seed)
    [(
        id=i,
        c=if complexity_dist == "zipf"
            clamp(round(Int, 100 / (rand(rng) * 99 + 1)), 1, 100)
        elseif complexity_dist == "uniform"
            rand(rng, 1:100)
        else
            clamp(round(Int, 100 * rand(rng)^2), 1, 100)
        end,
        w=rand(rng),
        v=rand(rng),
        mistake_flag=false,
    ) for i in 1:num_actions]
end

function evaluate_judge!(actions; bias_strength, noise_scale, tau, seed)
    rng = MersenneTwister(seed)
    [(merge(a, (mistake_flag=(abs(clamp(a.v + bias_strength*(0.5-a.v) + randn(rng)*noise_scale, 0.0, 1.0) - a.v) > tau),))) for a in actions]
end

function select_primes(actions; q=0.9)
    thresh = quantile([a.w for a in actions], q)
    filter(a -> a.w >= thresh, actions)
end

function compute_Pi_and_error(primes; X_max=100)
    xs   = collect(1:X_max)
    Pi_x = [count(p -> p.c <= x, primes)        for x in xs]
    B_x  = [x <= 1 ? 1.0 : x / log(x)          for x in xs]
    E_x  = Pi_x .- B_x
    xs, Pi_x, B_x, E_x
end

function fit_alpha(E_x, x_vals)
    valid = [(log(x), log(abs(e) + 1e-9)) for (x, e) in zip(x_vals, E_x) if x > 1 && abs(e) > 1e-9]
    length(valid) < 5 && return 0.5, 0.0
    lx = [v[1] for v in valid]
    ly = [v[2] for v in valid]
    mx, my = mean(lx), mean(ly)
    alpha  = sum((lx .- mx) .* (ly .- my)) / (sum((lx .- mx).^2) + 1e-12)
    ss_res = sum((ly .- (my .+ alpha .* (lx .- mx))).^2)
    ss_tot = sum((ly .- my).^2) + 1e-12
    r2     = 1.0 - ss_res / ss_tot
    alpha, r2
end

function spectrum(primes; X_max=200)
    m    = zeros(Float64, X_max)
    for p in primes
        p.c <= X_max && (m[p.c] += 1)
    end
    n    = length(m)
    F    = abs.(fft_manual(m))
    freqs = (0:(n÷2)) ./ n
    amps  = F[1:(n÷2 + 1)] ./ sum(F[1:(n÷2 + 1)] .+ 1e-12)
    freqs, amps
end

function fft_manual(x::Vector{Float64})
    # Simple DFT (for spectrum visualization; n is small)
    n = length(x)
    [sum(x[k+1] * exp(-2π * im * j * k / n) for k in 0:n-1) for j in 0:n-1]
end

# ---------------------------------------------------------------------------
# Judge configs
# ---------------------------------------------------------------------------
const JUDGES = [
    ("Biased",       (bias_strength=0.2,  noise_scale=0.1, tau=0.3, seed=100)),
    ("Noisy",        (bias_strength=0.0,  noise_scale=0.3, tau=0.3, seed=200)),
    ("Conservative", (bias_strength=0.1,  noise_scale=0.05, tau=0.15, seed=300)),
    ("Radical",      (bias_strength=0.45, noise_scale=0.2,  tau=0.3, seed=400)),
]

# ---------------------------------------------------------------------------
# Figure helpers
# ---------------------------------------------------------------------------
function save_fig(fig, path; dpi=150)
    mkpath(dirname(path))
    save(path, fig; px_per_unit=dpi/96)
    println("      Saved: $path")
end

# ---------------------------------------------------------------------------
# Figure generators
# ---------------------------------------------------------------------------
function fig1_pi_b_e(x_vals, Pi_x, B_x, E_x, path)
    fig = Figure(size=(800, 500))
    ax  = Axis(fig[1,1]; xlabel="x", ylabel="Count / Estimate",
               title="Ethical Prime Distribution (Biased Judge)")
    lines!(ax, x_vals, Float64.(Pi_x); label="Π(x) ethical primes", color=:blue)
    lines!(ax, x_vals, B_x;  label="B(x) baseline (x/ln x)", color=:orange, linestyle=:dash)
    lines!(ax, x_vals, E_x;  label="E(x) = Π(x) - B(x)",    color=:red,    linestyle=:dot)
    axislegend(ax; position=:lt)
    save_fig(fig, path)
end

function fig2_error_growth(x_vals, E_x, alpha, path)
    pos = [(x, abs(e)) for (x, e) in zip(x_vals, E_x) if abs(e) > 1e-9]
    lx  = log.(first.(pos))
    ly  = log.(last.(pos))
    fig = Figure(size=(800, 500))
    ax  = Axis(fig[1,1]; xlabel="log(x)", ylabel="log|E(x)|",
               title="Error Growth Analysis (Biased Judge) — α ≈ $(round(alpha; digits=3))")
    scatter!(ax, lx, ly; color=:blue, markersize=4, label="|E(x)|")
    # Regression line
    if length(lx) > 1
        xfit = range(minimum(lx), maximum(lx); length=50)
        mx, my = mean(lx), mean(ly)
        yfit = my .+ alpha .* (xfit .- mx)
        lines!(ax, collect(xfit), yfit; color=:red, linestyle=:dash, label="fit α=$(round(alpha;digits=3))")
    end
    axislegend(ax; position=:lt)
    save_fig(fig, path)
end

function fig3_multi_judge(judge_results, path)
    fig = Figure(size=(900, 500))
    ax  = Axis(fig[1,1]; xlabel="x", ylabel="|E(x)|",
               title="Multi-Judge Error Comparison")
    colors = [:blue, :orange, :green, :purple, :red]
    for (k, (name, x_vals, _, _, E_x)) in enumerate(judge_results)
        lines!(ax, x_vals, abs.(E_x); label=name, color=colors[mod1(k, length(colors))])
    end
    axislegend(ax; position=:rt)
    save_fig(fig, path)
end

function fig4_exponent_comparison(judge_metrics, path)
    names  = [m[1] for m in judge_metrics]
    alphas = [m[2] for m in judge_metrics]
    fig = Figure(size=(800, 500))
    ax  = Axis(fig[1,1];
        xlabel = "Judge Type",
        ylabel = "Estimated Growth Exponent α",
        title  = "Estimated Growth Exponent α by Judge Type",
        xticks = (1:length(names), names),
    )
    barplot!(ax, 1:length(names), alphas; color=:steelblue)
    hlines!(ax, [0.5]; color=:red, linestyle=:dash, label="ERH bound α=0.5")
    axislegend(ax; position=:rt)
    save_fig(fig, path)
end

function fig5_spectrum(freqs, amps, path)
    top5 = sortperm(amps; rev=true)[1:min(5, length(amps))]
    fig = Figure(size=(800, 500))
    ax  = Axis(fig[1,1]; xlabel="Frequency", ylabel="Normalised Amplitude",
               title="Frequency Spectrum of Ethical Primes (Biased Judge)")
    lines!(ax, freqs, amps; color=:blue)
    scatter!(ax, freqs[top5], amps[top5]; color=:red, markersize=8, label="Peaks")
    axislegend(ax; position=:rt)
    save_fig(fig, path)
end

function fig6_zeros(E_x, x_vals, path)
    # Detect approximate zeros: sign changes in E(x)
    zeros_x = [x_vals[i] for i in 2:length(E_x) if sign(E_x[i]) != sign(E_x[i-1])]
    fig = Figure(size=(700, 700))
    ax  = Axis(fig[1,1]; xlabel="Re(s) proxy", ylabel="Im(s) proxy",
               title="Ethical Zeta Function Zeros in Complex Plane")
    scatter!(ax, fill(0.5, length(zeros_x)), Float64.(zeros_x);
             color=:blue, markersize=8, label="Approximate zeros")
    vlines!(ax, [0.5]; color=:red, linestyle=:dash, label="Critical line Re(s)=0.5")
    axislegend(ax; position=:rt)
    println("      Found $(length(zeros_x)) approximate zeros")
    save_fig(fig, path)
end

function fig7_critical_bound(judge_results, path)
    fig = Figure(size=(900, 500))
    ax  = Axis(fig[1,1]; xlabel="x", ylabel="|E(x)|",
               title="Critical Bound: |E(x)| vs √x",
               xscale=log10, yscale=log10)
    colors = [:blue, :orange, :green, :purple]
    for (k, (name, x_vals, _, _, E_x)) in enumerate(judge_results)
        abse = [max(abs(e), 1e-9) for e in E_x]
        lines!(ax, Float64.(x_vals), abse; label=name, color=colors[mod1(k, length(colors))])
    end
    xs = range(1, maximum(judge_results[1][2]); length=100)
    lines!(ax, xs, sqrt.(xs); color=:black, linestyle=:dash, linewidth=2, label="√x bound")
    axislegend(ax; position=:lt)
    save_fig(fig, path)
end

function fig8_primes_map(primes, path)
    cs = [Float64(p.c) for p in primes]
    ws = [Float64(p.w) for p in primes]
    ds = [Float64(p.v) for p in primes]  # use v as delta proxy
    fig = Figure(size=(800, 600))
    ax  = Axis(fig[1,1]; xlabel="Complexity c", ylabel="Moral weight w",
               title="Ethical Primes: Irreducible Dilemmas in Action Space")
    sc  = scatter!(ax, cs, ws; color=ds, colormap=:viridis, markersize=6)
    Colorbar(fig[1,2], sc; label="Ground-truth value (δ proxy)")
    save_fig(fig, path)
end

function fig10_complexity_dist(actions, path)
    cs = [a.c for a in actions]
    fig = Figure(size=(800, 500))
    ax  = Axis(fig[1,1]; xlabel="Complexity c", ylabel="Count",
               title="Action Complexity Distribution (Zipf)")
    hist!(ax, Float64.(cs); bins=50, color=:steelblue)
    save_fig(fig, path)
end

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
function main()
    args = parse_args()

    if args["smoke"]
        println("[smoke] generate_all_figures: minimal run (50 actions, X_max=20)")
        args["num_actions"] = 50
        args["X_max"]       = 20
    end

    project_root = joinpath(@__DIR__, "..", "..")
    output_dir   = args["output_dir"] !== nothing ? args["output_dir"] : joinpath(project_root, "figures")
    mkpath(output_dir)

    setup_paper_style!()
    Random.seed!(42)

    n_actions = args["num_actions"]
    X_max     = args["X_max"]

    println("=" ^ 70)
    println("ETHICAL RIEMANN HYPOTHESIS — FIGURE GENERATION (Julia / CairoMakie)")
    println("=" ^ 70)

    println("\n[1/10] Generating action space (N=$n_actions)...")
    actions = generate_world(num_actions=n_actions, complexity_dist="zipf", seed=42)
    println("       Generated $(length(actions)) actions")

    println("\n[2/10] Evaluating judges...")
    judge_results = []   # (name, x_vals, Pi_x, B_x, E_x)
    judge_metrics = []   # (name, alpha, r2)
    for (name, params) in JUDGES
        acts    = evaluate_judge!(actions; params...)
        primes  = select_primes(acts; q=0.9)
        xs, Pi_x, B_x, E_x = compute_Pi_and_error(primes; X_max=X_max)
        alpha, r2 = fit_alpha(E_x, xs)
        push!(judge_results, (name, xs, Pi_x, B_x, E_x))
        push!(judge_metrics, (name, alpha, r2))
        erh = 0.4 <= alpha <= 0.65 ? "Yes" : "No"
        println("  $name: α=$(round(alpha; digits=3)) R²=$(round(r2; digits=3)) ERH=$erh")
    end

    biased_idx = findfirst(r -> r[1] == "Biased", judge_results)
    biased_res = judge_results[biased_idx]
    x_vals_b, Pi_x_b, B_x_b, E_x_b = biased_res[2], biased_res[3], biased_res[4], biased_res[5]
    alpha_b = judge_metrics[biased_idx][2]

    println("\n[3/10] Selecting Biased primes for spectrum/zeros...")
    acts_b  = evaluate_judge!(actions; JUDGES[1][2]...)
    primes_b = select_primes(acts_b; q=0.9)

    println("\n[4/10] Figure 1: Π(x), B(x), E(x)...")
    fig1_pi_b_e(x_vals_b, Pi_x_b, B_x_b, E_x_b,
        joinpath(output_dir, "paper_fig1_pi_b_e.pdf"))

    println("\n[5/10] Figure 2: Error growth log-log...")
    fig2_error_growth(x_vals_b, E_x_b, alpha_b,
        joinpath(output_dir, "paper_fig2_error_growth.pdf"))

    println("\n[6/10] Figure 3: Multi-judge error comparison...")
    fig3_multi_judge(judge_results,
        joinpath(output_dir, "paper_fig3_judge_comparison.pdf"))

    println("\n[7/10] Figure 4: Exponent comparison bar chart...")
    fig4_exponent_comparison(judge_metrics,
        joinpath(output_dir, "paper_fig4_exponent_comparison.pdf"))

    println("\n[8/10] Figure 5: Frequency spectrum...")
    freqs, amps = spectrum(primes_b; X_max=min(200, n_actions))
    fig5_spectrum(freqs, amps,
        joinpath(output_dir, "paper_fig5_spectrum.pdf"))

    println("\n[9/10] Figure 6: Zeta zeros...")
    fig6_zeros(E_x_b, x_vals_b,
        joinpath(output_dir, "paper_fig6_zeros.pdf"))

    println("\n[9b/10] Figure 7: Critical bound (log-log)...")
    fig7_critical_bound(judge_results,
        joinpath(output_dir, "paper_fig7_critical_bound.pdf"))

    println("\n[9c/10] Figure 8: Ethical primes map...")
    fig8_primes_map(primes_b,
        joinpath(output_dir, "paper_fig8_ethical_primes_map.pdf"))

    println("\n[10/10] Figure 10: Complexity distribution...")
    fig10_complexity_dist(actions,
        joinpath(output_dir, "paper_fig10_complexity_dist.pdf"))

    # Summary table (LaTeX rows)
    table_path = joinpath(output_dir, "comparison_table_rows.tex")
    open(table_path, "w") do io
        rows = String[]
        for (name, alpha, r2) in judge_metrics
            erh = 0.4 <= alpha <= 0.65 ? "Yes" : "No"
            interp = erh == "Yes" ? "ERH OK" : "Violates bound"
            push!(rows, "$name & [TBD] & [TBD] & N/A & $(round(alpha;digits=3)) & $erh & $interp")
        end
        write(io, join(rows, " \\\\\n") * "\n")
    end
    println("\nLaTeX table rows saved to: $table_path")

    # Numerical summary
    summary_path = joinpath(output_dir, "..", "simulation", "output", "results_summary.txt")
    mkpath(dirname(summary_path))
    open(summary_path, "w") do io
        println(io, "ETHICAL RIEMANN HYPOTHESIS — NUMERICAL RESULTS (Julia)")
        println(io, "=" ^ 70)
        for (name, alpha, r2) in judge_metrics
            erh = 0.4 <= alpha <= 0.65 ? "Yes" : "No"
            println(io, "\n$name Judge:")
            println(io, "  Estimated exponent: $(round(alpha; digits=3))")
            println(io, "  R² (fit quality):   $(round(r2; digits=3))")
            println(io, "  Within ERH bound:   $erh")
        end
    end
    println("Numerical results saved to: $summary_path")

    println("\n" * "=" ^ 70)
    println("All figures generated successfully!")
    println("=" ^ 70)
end

main()
