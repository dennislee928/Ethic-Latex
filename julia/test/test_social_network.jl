"""
Tests for SocialNetwork.jl — covers all topology constructors, graph statistics,
centrality measures, community detection, and all opinion dynamics models
(DeGroot, Hegselmann-Krause, aggregate_beliefs, simulate_opinion_evolution).
"""

@testset "SocialNetwork" begin

    import ..SocialNetwork as SN

    # Helper: build a small network for repeated use
    function small_net(n=10; topology="small_world", seed=1)
        ids    = collect(1:n)
        errors = fill(0.1, n)
        tendencies = range(0.2, 0.8, length=n) |> collect
        SN.create_network(ids, errors, tendencies; topology=topology, seed=seed)
    end

    # -----------------------------------------------------------------------
    # 1. Network creation — all topologies
    # -----------------------------------------------------------------------
    @testset "topology constructors" begin
        using Graphs: nv, ne

        for topo in ("random", "small_world", "scale_free", "star", "ring", "complete")
            net = small_net(8; topology=topo)
            @test nv(net.graph) == 8
            @test length(net.nodes) == 8
            @test length(net.agent_to_node) == 8
        end

        # Complete graph has n(n-1)/2 edges
        net_c = small_net(6; topology="complete")
        @test ne(net_c.graph) == 6*5÷2

        # Star: exactly n-1 edges
        net_s = small_net(7; topology="star")
        @test ne(net_s.graph) == 6
    end

    # -----------------------------------------------------------------------
    # 2. add_node! / add_edge!
    # -----------------------------------------------------------------------
    @testset "add_node! and add_edge!" begin
        net = small_net(5; topology="ring")
        original_n = length(net.nodes)
        SN.add_node!(net, 999, 0.05, 0.6)
        @test length(net.nodes) == original_n + 1
        @test net.agent_to_node[999] == original_n + 1

        SN.add_edge!(net, 1, 999, 0.75)
        @test SN.get_influence_strength(net, 1, 999) ≈ 0.75
    end

    # -----------------------------------------------------------------------
    # 3. get_neighbors
    # -----------------------------------------------------------------------
    @testset "get_neighbors" begin
        net = small_net(6; topology="ring")
        nbrs = SN.get_neighbors(net, 1)
        # Ring: node 1 connects to node 2 and node 6
        @test length(nbrs) == 2
        @test 2 ∈ nbrs
        @test 6 ∈ nbrs

        # Unknown agent → empty
        @test isempty(SN.get_neighbors(net, 9999))
    end

    # -----------------------------------------------------------------------
    # 4. get_influence_strength
    # -----------------------------------------------------------------------
    @testset "get_influence_strength" begin
        net = small_net(6; topology="complete")
        # All pairs connected, default weight = 1.0
        @test SN.get_influence_strength(net, 1, 3) ≈ 1.0

        # Add custom weight
        SN.add_edge!(net, 1, 3, 2.5)
        @test SN.get_influence_strength(net, 1, 3) ≈ 2.5

        # Non-connected pair in a star (leaf to leaf)
        net_s = small_net(5; topology="star")
        @test SN.get_influence_strength(net_s, 2, 3) == 0.0
    end

    # -----------------------------------------------------------------------
    # 5. get_adjacency_submatrix
    # -----------------------------------------------------------------------
    @testset "get_adjacency_submatrix" begin
        net = small_net(6; topology="complete")
        M = SN.get_adjacency_submatrix(net, 4)
        @test size(M) == (4, 4)
        # Symmetric
        @test M ≈ M'
        # Diagonal is zero
        @test all(M[i,i] == 0 for i in 1:4)
        # All off-diagonal entries in a complete graph are ≥ 1
        for i in 1:4, j in 1:4
            i == j && continue
            @test M[i,j] >= 1.0
        end
    end

    # -----------------------------------------------------------------------
    # 6. update_node_attributes!
    # -----------------------------------------------------------------------
    @testset "update_node_attributes!" begin
        net = small_net(4; topology="ring")
        new_errors     = [0.9, 0.8, 0.7, 0.6]
        new_tendencies = [0.1, 0.2, 0.3, 0.4]
        SN.update_node_attributes!(net, collect(1:4), new_errors, new_tendencies)
        @test net.nodes[1].error_rate        ≈ 0.9
        @test net.nodes[4].judgment_tendency ≈ 0.4
    end

    # -----------------------------------------------------------------------
    # 7. get_network_statistics
    # -----------------------------------------------------------------------
    @testset "get_network_statistics" begin
        net = small_net(10; topology="small_world")
        stats = SN.get_network_statistics(net)
        @test stats["num_nodes"] == 10
        @test stats["num_edges"] >= 0
        @test 0.0 <= stats["density"] <= 1.0
        @test stats["average_degree"] >= 0.0
        @test 0.0 <= stats["clustering_coefficient"] <= 1.0

        # Empty network
        empty_net = SN.SocialNetworkState(
            Graphs.SimpleGraph(0),
            SN.AgentNode[],
            Dict{Int,Int}(),
            Dict{Tuple{Int,Int},Float64}()
        )
        empty_stats = SN.get_network_statistics(empty_net)
        @test empty_stats["num_nodes"] == 0
    end

    # -----------------------------------------------------------------------
    # 8. get_centrality_measures
    # -----------------------------------------------------------------------
    @testset "get_centrality_measures" begin
        net = small_net(6; topology="complete")
        centrality = SN.get_centrality_measures(net)
        @test length(centrality) == 6
        for (aid, measures) in centrality
            @test haskey(measures, "degree_centrality")
            @test haskey(measures, "betweenness_centrality")
            @test haskey(measures, "eigenvector_centrality")
            @test 0.0 <= measures["degree_centrality"] <= 1.0
        end
    end

    # -----------------------------------------------------------------------
    # 9. detect_communities
    # -----------------------------------------------------------------------
    @testset "detect_communities" begin
        net = small_net(8; topology="small_world", seed=5)
        comms = SN.detect_communities(net; seed=5)
        @test length(comms) == 8          # every agent gets a community id
        @test all(v -> v >= 0, values(comms))   # non-negative community ids
    end

    # -----------------------------------------------------------------------
    # 10. Opinion dynamics — DeGroot
    # -----------------------------------------------------------------------
    @testset "degroot_model!" begin
        net = small_net(10; topology="complete")
        # All same opinion → should converge immediately
        tendencies_same = fill(0.5, 10)
        r = SN.degroot_model!(tendencies_same, net; max_iterations=50)
        @test r.converged == true
        @test all(t -> isapprox(t, 0.5, atol=1e-5), r.final_opinions)

        # Mixed opinions → should converge for complete graph
        tendencies_mixed = range(0.0, 1.0, length=10) |> collect
        r2 = SN.degroot_model!(tendencies_mixed, net; max_iterations=200)
        @test r2.converged == true
        # All opinions should converge to a consensus value
        @test std(r2.final_opinions) < 0.01
    end

    # -----------------------------------------------------------------------
    # 11. Opinion dynamics — Hegselmann-Krause
    # -----------------------------------------------------------------------
    @testset "hegselmann_krause_model!" begin
        net = small_net(8; topology="complete")
        tendencies = range(0.3, 0.7, length=8) |> collect
        r = SN.hegselmann_krause_model!(tendencies, net;
                confidence_radius=0.5, max_iterations=100)
        @test r.converged == true
        @test !isempty(r.clusters)
        @test isa(r.final_opinions, Vector{Float64})

        # Confidence radius 0 → no opinion update (everyone stays isolated)
        tendencies2 = [0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9]
        r2 = SN.hegselmann_krause_model!(copy(tendencies2), net;
                confidence_radius=0.0, max_iterations=5)
        # No change → immediate "convergence"
        @test length(r2.clusters) > 1
    end

    # -----------------------------------------------------------------------
    # 12. detect_opinion_clusters
    # -----------------------------------------------------------------------
    @testset "detect_opinion_clusters" begin
        opinions = [0.1, 0.12, 0.5, 0.52, 0.9, 0.91]
        clusters = SN.detect_opinion_clusters(opinions, 0.05)
        @test length(clusters) == 3      # three distinct groups
        cluster_sizes = sort([length(c) for c in clusters])
        @test cluster_sizes == [2, 2, 2]
    end

    # -----------------------------------------------------------------------
    # 13. aggregate_beliefs!
    # -----------------------------------------------------------------------
    @testset "aggregate_beliefs!" begin
        net = small_net(6; topology="complete")
        individual_errors = Dict(i => 0.1 * i for i in 1:6)
        agg = SN.aggregate_beliefs!(individual_errors, net; dynamics_model="degroot")
        @test length(agg) == 6
        @test all(0.0 <= v <= 1.0 for v in values(agg))
    end

    # -----------------------------------------------------------------------
    # 14. compute_group_error
    # -----------------------------------------------------------------------
    @testset "compute_group_error" begin
        net = small_net(5; topology="complete")
        errs = Dict(i => 0.2 for i in 1:5)
        @test SN.compute_group_error(net, errs; aggregation_method="simple_average") ≈ 0.2
        @test SN.compute_group_error(net, errs; aggregation_method="max") ≈ 0.2
        @test SN.compute_group_error(net, errs; aggregation_method="min") ≈ 0.2

        errs2 = Dict(1 => 0.0, 2 => 0.5, 3 => 0.0, 4 => 0.5, 5 => 0.0)
        @test SN.compute_group_error(net, errs2; aggregation_method="simple_average") ≈ 0.2
    end

    # -----------------------------------------------------------------------
    # 15. simulate_opinion_evolution
    # -----------------------------------------------------------------------
    @testset "simulate_opinion_evolution" begin
        net = small_net(6; topology="complete")
        tendencies = range(0.0, 1.0, length=6) |> collect
        res = SN.simulate_opinion_evolution(tendencies, net; time_steps=30,
                                            dynamics_model="degroot")
        @test isa(res.opinion_history, Matrix)
        @test size(res.opinion_history, 2) == 6
        @test res.convergence_time !== nothing || !res.final_consensus
    end

end # @testset "SocialNetwork"
