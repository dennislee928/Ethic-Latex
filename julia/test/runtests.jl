using Test

@testset "ERH Julia Test Suite" begin
    # Phase 1 — Mathematical Core
    include("test_ethical_primes.jl")
    include("test_zeta_function.jl")
    include("test_erh_checks.jl")
    include("test_erh_statistics.jl")

    # Phase 2 — Simulation Framework
    include("test_abm_simulator.jl")
    include("test_social_network.jl")
    include("test_temporal_erh.jl")
    include("test_fluid_model.jl")

    # Phase 3 — Quantum Simulation
    include("test_quantum_simulator.jl")
    include("test_quantum_walk.jl")

    # Phase 4 — Scripts (smoke tests only)
    include("test_scripts_smoke.jl")
end
