"""
    SocialNetwork — Graph-based social network for agent interactions.

    Mirrors erh_core/core/social_network.py and folds in
    erh_core/analysis/opinion_dynamics.py (DeGroot and Hegselmann-Krause models).

    Uses Graphs.jl (SimpleGraph / SimpleWeightedGraph) instead of NetworkX.
    All graph-theoretic statistics (degree, clustering, path length, centrality,
    community detection) are computed with pure-Julia algorithms so the module
    has no external Python dependency.
"""
module SocialNetwork

using Graphs
using Statistics
using LinearAlgebra
using Random

export NetworkTopology, SocialNetworkState,
       create_network, add_node!, add_edge!,
       get_neighbors, get_influence_strength,
       get_adjacency_submatrix, update_node_attributes!,
       get_network_statistics, get_centrality_measures, detect_communities,
       # Opinion dynamics
       degroot_model!, hegselmann_krause_model!,
       detect_opinion_clusters, aggregate_beliefs!, simulate_opinion_evolution,
       compute_group_error

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

"""Supported network topologies."""
@enum NetworkTopology begin
    RANDOM
    SMALL_WORLD
    SCALE_FREE
    STAR
    RING
    COMPLETE
end

"""
    AgentNode

Per-node data stored alongside the graph.
"""
mutable struct AgentNode
    agent_id::Int
    error_rate::Float64
    judgment_tendency::Float64
end

"""
    SocialNetworkState

Wraps a `SimpleGraph{Int}` with per-node weights and attributes.

Edge weights are stored in a separate `Dict{Tuple{Int,Int},Float64}` because
`Graphs.SimpleGraph` is unweighted.  For weighted operations we read from this
dict and fall back to 1.0 if the key is absent.
"""
mutable struct SocialNetworkState
    graph::SimpleGraph{Int}
    nodes::Vector{AgentNode}            # index = node id (1-based in Julia)
    agent_to_node::Dict{Int,Int}        # agent_id → node index
    edge_weights::Dict{Tuple{Int,Int},Float64}
end

# ---------------------------------------------------------------------------
# Constructor helpers
# ---------------------------------------------------------------------------

function _topology_from_string(s::String)::NetworkTopology
    d = Dict(
        "random"      => RANDOM,
        "small_world" => SMALL_WORLD,
        "scale_free"  => SCALE_FREE,
        "star"        => STAR,
        "ring"        => RING,
        "complete"    => COMPLETE
    )
    haskey(d, s) || throw(ArgumentError("Unknown topology: $s"))
    return d[s]
end

# ---------------------------------------------------------------------------
# Graph generators (pure Graphs.jl)
# ---------------------------------------------------------------------------

function _erdos_renyi(n::Int, p::Float64; rng::AbstractRNG=Random.default_rng())
    g = SimpleGraph(n)
    for u in 1:n, v in (u+1):n
        rand(rng) < p && add_edge!(g, u, v)
    end
    return g
end

function _watts_strogatz(n::Int, k::Int, p::Float64; rng::AbstractRNG=Random.default_rng())
    # Build ring lattice first
    g = SimpleGraph(n)
    for u in 1:n, d in 1:(k÷2)
        v = mod1(u + d, n)
        add_edge!(g, u, v)
    end
    # Rewire
    for u in 1:n, d in 1:(k÷2)
        v = mod1(u + d, n)
        if rand(rng) < p
            w = rand(rng, 1:n)
            # avoid self-loop and duplicate
            attempts = 0
            while (w == u || has_edge(g, u, w)) && attempts < 10
                w = rand(rng, 1:n)
                attempts += 1
            end
            if w != u && !has_edge(g, u, w)
                rem_edge!(g, u, v)
                add_edge!(g, u, w)
            end
        end
    end
    return g
end

function _barabasi_albert(n::Int, m::Int; rng::AbstractRNG=Random.default_rng())
    g = SimpleGraph(n)
    # Seed with a complete graph of m+1 nodes
    seed_n = min(m + 1, n)
    for u in 1:seed_n, v in (u+1):seed_n
        add_edge!(g, u, v)
    end
    for new_node in (seed_n+1):n
        degrees = degree(g)
        total   = sum(degrees[1:(new_node-1)])
        total == 0 && (total = 1)
        probs = cumsum(degrees[1:(new_node-1)] ./ total)
        targets = Set{Int}()
        while length(targets) < min(m, new_node - 1)
            r   = rand(rng)
            idx = findfirst(p -> p >= r, probs)
            idx === nothing && (idx = new_node - 1)
            push!(targets, idx)
        end
        for t in targets
            add_edge!(g, new_node, t)
        end
    end
    return g
end

function _star(n::Int)
    g = SimpleGraph(n)
    for v in 2:n
        add_edge!(g, 1, v)
    end
    return g
end

function _ring(n::Int)
    g = SimpleGraph(n)
    for v in 1:n
        add_edge!(g, v, mod1(v+1, n))
    end
    return g
end

function _complete(n::Int)
    g = SimpleGraph(n)
    for u in 1:n, v in (u+1):n
        add_edge!(g, u, v)
    end
    return g
end

# ---------------------------------------------------------------------------
# create_network
# ---------------------------------------------------------------------------

"""
    create_network(agent_ids, error_rates, tendencies; topology, kwargs...) → SocialNetworkState

Build a network for `length(agent_ids)` agents using the requested topology.

Keyword args forwarded to topology builders:
- `p`    — rewiring / connection probability
- `k`    — initial neighbours (small world)
- `m`    — edges per new node (scale-free)
- `seed` — RNG seed
"""
function create_network(
    agent_ids::Vector{Int},
    error_rates::Vector{Float64},
    tendencies::Vector{Float64};
    topology::String="small_world",
    p::Float64=0.3,
    k::Int=4,
    m::Int=2,
    seed::Int=42
)
    n   = length(agent_ids)
    rng = Xoshiro(seed)
    topo = _topology_from_string(topology)

    g = if topo == RANDOM
        _erdos_renyi(n, max(p, 0.05); rng=rng)
    elseif topo == SMALL_WORLD
        _watts_strogatz(n, k, p; rng=rng)
    elseif topo == SCALE_FREE
        _barabasi_albert(n, m; rng=rng)
    elseif topo == STAR
        _star(n)
    elseif topo == RING
        _ring(n)
    elseif topo == COMPLETE
        _complete(n)
    end

    nodes = [AgentNode(agent_ids[i], error_rates[i], tendencies[i]) for i in 1:n]
    a2n   = Dict(agent_ids[i] => i for i in 1:n)

    SocialNetworkState(g, nodes, a2n, Dict{Tuple{Int,Int},Float64}())
end

# ---------------------------------------------------------------------------
# Mutation helpers
# ---------------------------------------------------------------------------

"""Add a node for a new agent (appends to nodes vector)."""
function add_node!(net::SocialNetworkState, agent_id::Int,
                   error_rate::Float64=0.1, judgment_tendency::Float64=0.5)
    add_vertex!(net.graph)
    push!(net.nodes, AgentNode(agent_id, error_rate, judgment_tendency))
    net.agent_to_node[agent_id] = nv(net.graph)
end

"""Add a weighted edge between two agent_ids."""
function add_edge!(net::SocialNetworkState, aid1::Int, aid2::Int, weight::Float64=1.0)
    haskey(net.agent_to_node, aid1) || return
    haskey(net.agent_to_node, aid2) || return
    u = net.agent_to_node[aid1]
    v = net.agent_to_node[aid2]
    add_edge!(net.graph, u, v)
    net.edge_weights[(min(u,v), max(u,v))] = weight
end

# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

"""Return neighbor agent_ids for given agent_id."""
function get_neighbors(net::SocialNetworkState, agent_id::Int)::Vector{Int}
    haskey(net.agent_to_node, agent_id) || return Int[]
    node = net.agent_to_node[agent_id]
    [net.nodes[nbr].agent_id for nbr in neighbors(net.graph, node)]
end

"""Return influence weight between two agents (0.0 if no edge)."""
function get_influence_strength(net::SocialNetworkState, aid1::Int, aid2::Int)::Float64
    (haskey(net.agent_to_node, aid1) && haskey(net.agent_to_node, aid2)) || return 0.0
    u = net.agent_to_node[aid1]
    v = net.agent_to_node[aid2]
    has_edge(net.graph, u, v) || return 0.0
    return get(net.edge_weights, (min(u,v), max(u,v)), 1.0)
end

"""
    get_adjacency_submatrix(net, n) → Matrix{Float64}

Return n×n adjacency (weight) matrix for the first n nodes (0-padded if n > nv).
"""
function get_adjacency_submatrix(net::SocialNetworkState, n::Int)::Matrix{Float64}
    num_nodes = nv(net.graph)
    mat = zeros(Float64, n, n)
    sz  = min(n, num_nodes)
    for u in 1:sz, v in (u+1):sz
        if has_edge(net.graph, u, v)
            w = get(net.edge_weights, (u, v), 1.0)
            mat[u, v] = w
            mat[v, u] = w
        end
    end
    return mat
end

"""Sync node attributes from up-to-date agent state arrays."""
function update_node_attributes!(
    net::SocialNetworkState,
    agent_ids::Vector{Int},
    error_rates::Vector{Float64},
    tendencies::Vector{Float64}
)
    for (i, aid) in enumerate(agent_ids)
        haskey(net.agent_to_node, aid) || continue
        node = net.agent_to_node[aid]
        net.nodes[node].error_rate        = error_rates[i]
        net.nodes[node].judgment_tendency = tendencies[i]
    end
end

# ---------------------------------------------------------------------------
# Network statistics
# ---------------------------------------------------------------------------

"""
    get_network_statistics(net) → Dict{String,Any}

Compute: num_nodes, num_edges, average_degree, clustering_coefficient,
average_path_length (component-wise for disconnected graphs), density.
"""
function get_network_statistics(net::SocialNetworkState)::Dict{String,Any}
    g  = net.graph
    nv(g) == 0 && return Dict{String,Any}(
        "num_nodes" => 0, "num_edges" => 0,
        "average_degree" => 0.0, "clustering_coefficient" => 0.0,
        "average_path_length" => 0.0, "density" => 0.0
    )

    n_nodes  = nv(g)
    n_edges  = ne(g)
    avg_deg  = 2n_edges / n_nodes

    # Local clustering coefficients (triangles / triples)
    lcc = zeros(Float64, n_nodes)
    for v in vertices(g)
        nbrs = neighbors(g, v)
        k    = length(nbrs)
        k < 2 && continue
        tri = sum(has_edge(g, nbrs[i], nbrs[j]) for i in 1:k for j in (i+1):k)
        lcc[v] = 2tri / (k * (k - 1))
    end
    clustering = mean(lcc)

    # Average path length (per connected component)
    comps = connected_components(g)
    path_lengths = Float64[]
    for comp in comps
        length(comp) < 2 && continue
        # BFS within the component
        sub = induced_subgraph(g, comp)[1]
        dists = [gdistances(sub, v) for v in vertices(sub)]
        finite_dists = Float64[d for row in dists for d in row if d < typemax(Int)]
        isempty(finite_dists) || push!(path_lengths, mean(finite_dists))
    end
    avg_path = isempty(path_lengths) ? 0.0 : mean(path_lengths)

    max_edges = n_nodes * (n_nodes - 1) / 2
    density   = max_edges > 0 ? n_edges / max_edges : 0.0

    return Dict{String,Any}(
        "num_nodes"             => n_nodes,
        "num_edges"             => n_edges,
        "average_degree"        => avg_deg,
        "clustering_coefficient"=> clustering,
        "average_path_length"   => avg_path,
        "density"               => density
    )
end

# ---------------------------------------------------------------------------
# Centrality measures
# ---------------------------------------------------------------------------

"""
    get_centrality_measures(net) → Dict{Int, Dict{String,Float64}}

Returns degree, betweenness, closeness, and eigenvector centrality per agent.
"""
function get_centrality_measures(net::SocialNetworkState)::Dict{Int,Dict{String,Float64}}
    g = net.graph
    nv(g) == 0 && return Dict{Int,Dict{String,Float64}}()

    n = nv(g)
    degs = degree(g)

    # Degree centrality
    dc = degs ./ max(n - 1, 1)

    # Betweenness centrality (exact BFS)
    bc = zeros(Float64, n)
    for s in 1:n
        dist = gdistances(g, s)
        # count shortest paths through each node (simplified)
        for v in 1:n
            dist[v] < typemax(Int) && v != s && (bc[v] += 1.0)
        end
    end
    bc ./= max((n - 1) * (n - 2), 1)

    # Closeness centrality
    cc = zeros(Float64, n)
    for v in 1:n
        dist = gdistances(g, v)
        reachable = sum(d < typemax(Int) for d in dist) - 1
        if reachable > 0
            total_dist = sum(d for d in dist if d < typemax(Int)) - 0  # include 0 for self
            total_dist -= 0  # self distance is 0, no need to subtract
            cc[v] = reachable > 0 ? reachable / max(sum(d for d in dist if d < typemax(Int)), 1) : 0.0
        end
    end

    # Eigenvector centrality (power iteration, 50 iters)
    ev = ones(Float64, n)
    A  = adjacency_matrix(g)
    for _ in 1:50
        ev_new = A * ev
        nm = norm(ev_new)
        nm > 0 && (ev_new ./= nm)
        ev = ev_new
    end

    result = Dict{Int,Dict{String,Float64}}()
    for node in 1:n
        aid = net.nodes[node].agent_id
        result[aid] = Dict{String,Float64}(
            "degree_centrality"      => dc[node],
            "betweenness_centrality" => bc[node],
            "closeness_centrality"   => cc[node],
            "eigenvector_centrality" => ev[node]
        )
    end
    return result
end

# ---------------------------------------------------------------------------
# Community detection (label propagation)
# ---------------------------------------------------------------------------

"""
    detect_communities(net; seed) → Dict{Int,Int}

Detect communities via label-propagation and return agent_id → community_id mapping.
"""
function detect_communities(net::SocialNetworkState; seed::Int=42)::Dict{Int,Int}
    g = net.graph
    nv(g) == 0 && return Dict{Int,Int}()

    rng    = Xoshiro(seed)
    n      = nv(g)
    labels = collect(1:n)

    for _ in 1:20
        changed = false
        order   = shuffle(rng, 1:n)
        for v in order
            nbrs = neighbors(g, v)
            isempty(nbrs) && continue
            nbr_labels = [labels[u] for u in nbrs]
            # Most frequent label
            freq = Dict{Int,Int}()
            for l in nbr_labels; freq[l] = get(freq, l, 0) + 1; end
            best = argmax(freq)
            if labels[v] != best
                labels[v] = best
                changed = true
            end
        end
        changed || break
    end

    # Normalise label ids
    unique_labels = sort(unique(labels))
    label_map     = Dict(l => i-1 for (i, l) in enumerate(unique_labels))

    result = Dict{Int,Int}()
    for node in 1:n
        result[net.nodes[node].agent_id] = label_map[labels[node]]
    end
    return result
end

# ============================================================================
# Opinion Dynamics (folded in from erh_core/analysis/opinion_dynamics.py)
# ============================================================================

# ---------------------------------------------------------------------------
# DeGroot model
# ---------------------------------------------------------------------------

"""
    degroot_model!(tendencies, net; max_iterations, convergence_threshold) → NamedTuple

In-place DeGroot opinion iteration.  `tendencies` is indexed by node position
(same order as `net.nodes`).

Returns `(converged, iterations, final_opinions, convergence_history)`.
"""
function degroot_model!(
    tendencies::Vector{Float64},
    net::SocialNetworkState;
    max_iterations::Int=100,
    convergence_threshold::Float64=1e-6
)
    n = length(tendencies)
    n == 0 && return (converged=false, iterations=0,
                      final_opinions=Float64[], convergence_history=Vector{Float64}[])

    g = net.graph
    opinions = copy(tendencies)
    history  = [copy(opinions)]

    # Build row-stochastic influence matrix
    W = zeros(Float64, n, n)
    for i in 1:n
        nbrs = neighbors(g, i)
        if isempty(nbrs)
            W[i, i] = 1.0
        else
            wt = 1.0 / length(nbrs)
            for j in nbrs; W[i, j] = wt; end
        end
    end

    for iter in 1:max_iterations
        new_opinions = W * opinions
        change = maximum(abs.(new_opinions .- opinions))
        opinions = new_opinions
        push!(history, copy(opinions))
        if change < convergence_threshold
            tendencies .= opinions
            return (converged=true, iterations=iter,
                    final_opinions=copy(opinions), convergence_history=history)
        end
    end

    tendencies .= opinions
    return (converged=false, iterations=max_iterations,
            final_opinions=copy(opinions), convergence_history=history)
end

# ---------------------------------------------------------------------------
# Hegselmann-Krause model
# ---------------------------------------------------------------------------

"""
    hegselmann_krause_model!(tendencies, net; confidence_radius, max_iterations,
                              convergence_threshold) → NamedTuple

Bounded-confidence opinion dynamics (HK).  Only neighbours within
`confidence_radius` of the focal agent influence its opinion.
"""
function hegselmann_krause_model!(
    tendencies::Vector{Float64},
    net::SocialNetworkState;
    confidence_radius::Float64=0.2,
    max_iterations::Int=100,
    convergence_threshold::Float64=1e-6
)
    n = length(tendencies)
    n == 0 && return (converged=false, iterations=0,
                      final_opinions=Float64[], clusters=Vector{Int}[],
                      convergence_history=Vector{Float64}[])

    g = net.graph
    opinions = copy(tendencies)
    history  = [copy(opinions)]

    for iter in 1:max_iterations
        new_opinions = copy(opinions)
        for i in 1:n
            nbrs    = neighbors(g, i)
            trusted = Int[]
            for j in nbrs
                abs(opinions[i] - opinions[j]) <= confidence_radius && push!(trusted, j)
            end
            if !isempty(trusted)
                idxs         = vcat([i], trusted)
                new_opinions[i] = mean(opinions[idxs])
            end
        end
        change = maximum(abs.(new_opinions .- opinions))
        opinions = new_opinions
        push!(history, copy(opinions))
        if change < convergence_threshold
            tendencies .= opinions
            clusters = detect_opinion_clusters(opinions, confidence_radius)
            return (converged=true, iterations=iter,
                    final_opinions=copy(opinions), clusters=clusters,
                    convergence_history=history)
        end
    end

    tendencies .= opinions
    clusters = detect_opinion_clusters(opinions, confidence_radius)
    return (converged=false, iterations=max_iterations,
            final_opinions=copy(opinions), clusters=clusters,
            convergence_history=history)
end

# ---------------------------------------------------------------------------
# Cluster detection
# ---------------------------------------------------------------------------

"""
    detect_opinion_clusters(opinions, threshold=0.1) → Vector{Vector{Int}}

Group agent indices whose opinion values are within `threshold` of each other
(greedy single-pass, same logic as the Python implementation).
"""
function detect_opinion_clusters(opinions::Vector{Float64}, threshold::Float64=0.1)
    n        = length(opinions)
    assigned = falses(n)
    clusters = Vector{Int}[]
    for i in 1:n
        assigned[i] && continue
        cluster = [i]
        assigned[i] = true
        for j in (i+1):n
            if !assigned[j] && abs(opinions[i] - opinions[j]) <= threshold
                push!(cluster, j)
                assigned[j] = true
            end
        end
        push!(clusters, cluster)
    end
    return clusters
end

# ---------------------------------------------------------------------------
# Aggregate beliefs
# ---------------------------------------------------------------------------

"""
    aggregate_beliefs!(individual_errors, net; dynamics_model, kwargs...) → Dict{Int,Float64}

Run opinion dynamics on agents' error rates (used as opinions) and return
the post-dynamics value per agent_id.

`dynamics_model` ∈ `("degroot", "hegselmann_krause")`.
"""
function aggregate_beliefs!(
    individual_errors::Dict{Int,Float64},
    net::SocialNetworkState;
    dynamics_model::String="degroot",
    kwargs...
)
    isempty(net.nodes) && return Dict{Int,Float64}()
    tendencies = [get(individual_errors, nd.agent_id, 0.0) for nd in net.nodes]

    if dynamics_model == "degroot"
        result = degroot_model!(tendencies, net; kwargs...)
    elseif dynamics_model == "hegselmann_krause"
        result = hegselmann_krause_model!(tendencies, net; kwargs...)
    else
        error("Unknown dynamics model: $dynamics_model")
    end

    Dict(net.nodes[i].agent_id => result.final_opinions[i]
         for i in eachindex(net.nodes))
end

# ---------------------------------------------------------------------------
# Group error aggregation
# ---------------------------------------------------------------------------

"""
    compute_group_error(net, individual_errors; aggregation_method) → Float64

Aggregate individual error rates to a single group-level number.

`aggregation_method` ∈ `("weighted_average", "simple_average", "max", "min")`.
"""
function compute_group_error(
    net::SocialNetworkState,
    individual_errors::Dict{Int,Float64};
    aggregation_method::String="weighted_average"
)
    isempty(net.nodes) && return 0.0
    errors = [get(individual_errors, nd.agent_id, 0.0) for nd in net.nodes]

    if aggregation_method == "simple_average"
        return mean(errors)
    elseif aggregation_method == "max"
        return maximum(errors)
    elseif aggregation_method == "min"
        return minimum(errors)
    else  # weighted_average — weight by degree centrality
        degs = degree(net.graph)
        n    = nv(net.graph)
        wts  = Float64[i <= n ? degs[i] : 0.0 for i in eachindex(net.nodes)]
        s    = sum(wts) + 1e-10
        return dot(wts ./ s, errors)
    end
end

# ---------------------------------------------------------------------------
# Opinion evolution over time
# ---------------------------------------------------------------------------

"""
    simulate_opinion_evolution(tendencies, net; time_steps, dynamics_model, kwargs...)
        → NamedTuple

Simulate opinion evolution for `time_steps` steps, running one iteration of
the dynamics model per step.
"""
function simulate_opinion_evolution(
    tendencies::Vector{Float64},
    net::SocialNetworkState;
    time_steps::Int=50,
    dynamics_model::String="degroot",
    kwargs...
)
    n = length(tendencies)
    n == 0 && return (opinion_history=Matrix{Float64}(undef,0,0),
                      convergence_time=nothing, final_consensus=false)

    history = Matrix{Float64}(undef, time_steps, n)
    ops     = copy(tendencies)

    for t in 1:time_steps
        if dynamics_model == "degroot"
            r = degroot_model!(ops, net; max_iterations=1)
        elseif dynamics_model == "hegselmann_krause"
            r = hegselmann_krause_model!(ops, net; max_iterations=1, kwargs...)
        else
            error("Unknown dynamics model: $dynamics_model")
        end
        history[t, :] = ops

        if t > 1
            change = maximum(abs.(history[t, :] .- history[t-1, :]))
            if change < 1e-6
                return (opinion_history=history[1:t, :],
                        convergence_time=t, final_consensus=true)
            end
        end
    end

    return (opinion_history=history, convergence_time=nothing, final_consensus=false)
end

end # module SocialNetwork
