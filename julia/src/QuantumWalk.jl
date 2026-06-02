"""
    QuantumWalk — Quantum Random Walk for Opinion Diffusion (Cancel Culture Model).

    Mirrors simulation/quantum/quantum_walk.py using matrix-based coin+shift operators.

    Classical walk: std ~ O(√t)
    Quantum walk:   std ~ O(t)   ← models rapid moral-panic spread

    Design (coin + shift operator pattern):
      State space: position ∈ {0..n_sites-1} × coin ∈ {0,1}
      State vector: length 2*n_sites, interleaved as [|p,0⟩, |p,1⟩] for each p.
      Coin operator C: Hadamard (or biased) acting on coin degree of freedom.
      Shift operator S: |p,0⟩ → |p-1,0⟩ (left), |p,1⟩ → |p+1,1⟩ (right).
      One step = S · (I_position ⊗ C).
"""
module QuantumWalk

using LinearAlgebra
using Statistics
using Random

export quantum_walk_step, quantum_walk_propagate, diffusion_spread
export simulate_cancel_culture_spread
export build_coin_operator, build_shift_operator

# ---------------------------------------------------------------------------
# Coin operators
# ---------------------------------------------------------------------------

"""
    hadamard_coin() -> Matrix{ComplexF64}

Standard 2×2 Hadamard coin: H = (1/√2) [[1,1],[1,-1]].
"""
function hadamard_coin()::Matrix{ComplexF64}
    return ComplexF64[1 1; 1 -1] ./ sqrt(2.0)
end

"""
    biased_coin(coin_bias) -> Matrix{ComplexF64}

Biased coin matrix with probability `coin_bias` toward left (|0⟩) movement.
C = [[√p, √(1-p)], [√(1-p), -√p]]
"""
function biased_coin(coin_bias::Float64)::Matrix{ComplexF64}
    p  = coin_bias
    q  = 1.0 - coin_bias
    return ComplexF64[sqrt(p) sqrt(q); sqrt(q) -sqrt(p)]
end

"""
    build_coin_operator(n_sites, coin_bias) -> Matrix{ComplexF64}

Full coin operator on 2*n_sites-dimensional state space.
Applies the 2×2 coin to the coin register at each position site independently.
"""
function build_coin_operator(n_sites::Int, coin_bias::Float64=0.5)::Matrix{ComplexF64}
    coin = abs(coin_bias - 0.5) < 1e-9 ? hadamard_coin() : biased_coin(coin_bias)
    d = 2 * n_sites
    C = zeros(ComplexF64, d, d)
    for p in 0:(n_sites-1)
        base = p * 2 + 1  # Julia 1-indexed
        C[base:base+1, base:base+1] .= coin
    end
    return C
end

"""
    build_shift_operator(n_sites) -> Matrix{ComplexF64}

Conditional shift operator on 2*n_sites-dimensional state space.
|p, coin=0⟩ → |p-1, 0⟩  (left shift, reflecting at boundaries)
|p, coin=1⟩ → |p+1, 1⟩  (right shift, reflecting at boundaries)
"""
function build_shift_operator(n_sites::Int)::Matrix{ComplexF64}
    d = 2 * n_sites
    S = zeros(ComplexF64, d, d)
    for p in 0:(n_sites-1)
        # coin=0 → shift left
        dest_left = p - 1
        if 0 <= dest_left < n_sites
            S[dest_left * 2 + 1, p * 2 + 1] = 1.0  # |dest,0⟩ ← |p,0⟩
        end
        # coin=1 → shift right
        dest_right = p + 1
        if 0 <= dest_right < n_sites
            S[dest_right * 2 + 2, p * 2 + 2] = 1.0  # |dest,1⟩ ← |p,1⟩
        end
    end
    return S
end

# ---------------------------------------------------------------------------
# Core walk step
# ---------------------------------------------------------------------------

"""
    quantum_walk_step(state, n_sites; coin_bias) -> Vector{ComplexF64}

Single step of Hadamard quantum walk on a line.

State layout: state[p*2+1] = amplitude for |p, coin=0⟩ (1-indexed).
              state[p*2+2] = amplitude for |p, coin=1⟩.

Uses coin operator then shift operator: ψ' = S · C · ψ.
"""
function quantum_walk_step(state::Vector{<:Complex}, n_sites::Int;
                            coin_bias::Float64=0.5)::Vector{ComplexF64}
    coin = abs(coin_bias - 0.5) < 1e-9 ? hadamard_coin() : biased_coin(coin_bias)
    new_state = zeros(ComplexF64, 2 * n_sites)

    for p in 0:(n_sites-1)
        amp0 = state[p * 2 + 1]
        amp1 = state[p * 2 + 2]
        abs(amp0) < 1e-15 && abs(amp1) < 1e-15 && continue

        # Apply coin to (amp0, amp1)
        coined = coin * [amp0; amp1]

        # Shift: coined[1] goes left (coin=0), coined[2] goes right (coin=1)
        dest_left  = p - 1
        dest_right = p + 1

        if 0 <= dest_left < n_sites
            new_state[dest_left * 2 + 1] += coined[1]
        end
        if 0 <= dest_right < n_sites
            new_state[dest_right * 2 + 2] += coined[2]
        end
    end
    return new_state
end

# ---------------------------------------------------------------------------
# Propagation
# ---------------------------------------------------------------------------

"""
    quantum_walk_propagate(; n_sites, steps, initial_site, coin_bias, seed)
        -> (probs, timesteps)

Propagate quantum walk and return position probability distribution.

Returns:
  probs[p, t+1]  = P(position=p at step t)   (1-indexed, shape n_sites × steps+1)
  timesteps      = 0:steps
"""
function quantum_walk_propagate(;
    n_sites::Int=31,
    steps::Int=10,
    initial_site::Union{Int,Nothing}=nothing,
    coin_bias::Float64=0.5,
    seed::Union{Int,Nothing}=nothing,
)::Tuple{Matrix{Float64}, Vector{Int}}

    init_pos = initial_site === nothing ? n_sites ÷ 2 : initial_site
    init_pos = clamp(init_pos, 0, n_sites - 1)

    state = zeros(ComplexF64, 2 * n_sites)
    state[init_pos * 2 + 1] = 1.0 + 0im  # |init_pos, coin=0⟩

    probs = zeros(Float64, n_sites, steps + 1)
    probs[init_pos + 1, 1] = 1.0  # t=0 (1-indexed position)

    for t in 1:steps
        state = quantum_walk_step(state, n_sites; coin_bias=coin_bias)
        for p in 0:(n_sites-1)
            probs[p + 1, t + 1] = abs2(state[p * 2 + 1]) + abs2(state[p * 2 + 2])
        end
    end

    return probs, collect(0:steps)
end

# ---------------------------------------------------------------------------
# Diffusion spread comparison
# ---------------------------------------------------------------------------

"""
    diffusion_spread(; n_sites, steps, classical, seed) -> (final_std, max_prob)

Compare classical vs quantum diffusion spread (std of distribution).

Classical: std ~ O(√t)
Quantum:   std ~ O(t)
"""
function diffusion_spread(;
    n_sites::Int=31,
    steps::Int=20,
    classical::Bool=false,
    seed::Union{Int,Nothing}=nothing,
)::Tuple{Float64,Float64}

    rng = seed === nothing ? Random.default_rng() : MersenneTwister(seed)
    center = n_sites ÷ 2

    if classical
        pos = center
        counts = zeros(Float64, n_sites)
        for _ in 1:steps
            pos += rand(rng) > 0.5 ? 1 : -1
            pos = clamp(pos, 0, n_sites - 1)
        end
        final_dist = zeros(Float64, n_sites)
        final_dist[pos + 1] = 1.0
    else
        probs, _ = quantum_walk_propagate(
            n_sites=n_sites, steps=steps, initial_site=center,
            coin_bias=0.5, seed=seed,
        )
        final_dist = probs[:, end]
    end

    s = sum(final_dist)
    s < 1e-15 && return (0.0, 0.0)
    final_dist ./= s

    x = collect(0.0:(n_sites-1))
    mean_pos = sum(x .* final_dist)
    variance = sum((x .- mean_pos) .^ 2 .* final_dist)
    std_dev = sqrt(variance)

    return (std_dev, maximum(final_dist))
end

# ---------------------------------------------------------------------------
# Cancel culture spread simulation
# ---------------------------------------------------------------------------

"""
    simulate_cancel_culture_spread(; n_agents, steps, initial_infected, quantum, seed)
        -> Dict

Simulate opinion / moral-panic spread using quantum or classical random walk.

Quantum walk: O(t) diffusion — models rapid viral spread.
Classical:    O(√t) diffusion — slower baseline.

Returns:
  - spread_at_step: Vector{Float64} — std of position distribution at each step
  - infected_fraction: Float64 — fraction of agents with prob > 0.01 at final step
  - quantum: Bool
"""
function simulate_cancel_culture_spread(;
    n_agents::Int=50,
    steps::Int=15,
    initial_infected::Int=1,
    quantum::Bool=true,
    seed::Union{Int,Nothing}=nothing,
)::Dict{String,Any}

    rng = seed === nothing ? Random.default_rng() : MersenneTwister(seed)

    spread_at_step = Float64[]
    infected_fraction = 0.0

    if quantum
        init_site = clamp(initial_infected, 0, n_agents - 1)
        probs, _ = quantum_walk_propagate(
            n_sites=n_agents, steps=steps, initial_site=init_site,
            coin_bias=0.5, seed=seed,
        )
        for t in 0:steps
            dist = probs[:, t + 1]
            s = sum(dist)
            s < 1e-15 && (push!(spread_at_step, 0.0); continue)
            dist_norm = dist ./ s
            x = collect(0.0:(n_agents-1))
            mean_pos = sum(x .* dist_norm)
            std_dev = sqrt(sum((x .- mean_pos) .^ 2 .* dist_norm))
            push!(spread_at_step, std_dev)
        end
        infected_fraction = sum(probs[:, end] .> 0.01) / n_agents

    else
        # Classical random walk diffusion
        state = zeros(Float64, n_agents)
        init_pos = clamp(initial_infected - 1, 0, n_agents - 1)
        state[init_pos + 1] = 1.0

        x = collect(0.0:(n_agents-1))
        for _ in 0:steps
            s = sum(state)
            if s < 1e-15
                push!(spread_at_step, 0.0)
            else
                dist_norm = state ./ s
                mean_pos = sum(x .* dist_norm)
                std_dev  = sqrt(sum((x .- mean_pos) .^ 2 .* dist_norm))
                push!(spread_at_step, std_dev)
            end
            # Diffuse step: each agent passes 50% to neighbors
            new_state = zeros(Float64, n_agents)
            for i in 1:n_agents
                i > 1       && (new_state[i-1] += 0.5 * state[i])
                i < n_agents && (new_state[i+1] += 0.5 * state[i])
            end
            state = new_state
        end
        infected_fraction = sum(state .> 0.01) / n_agents
    end

    return Dict{String,Any}(
        "spread_at_step"    => spread_at_step,
        "infected_fraction" => infected_fraction,
        "quantum"           => quantum,
    )
end

end # module QuantumWalk
