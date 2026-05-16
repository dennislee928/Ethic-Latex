"""
    ERH — Ethical Riemann Hypothesis Julia Package

    Single-module entry point. Each sub-module mirrors a Python counterpart
    in erh_core/ and can be called via PyJulia or as a standalone library.
"""
module ERH

# Phase 1 — Mathematical Core
include("EthicalPrimes.jl")
include("ZetaFunction.jl")
include("ERHChecks.jl")
include("ERHStatistics.jl")

# Phase 2 — Simulation Framework
include("ABMSimulator.jl")
include("SocialNetwork.jl")
include("TemporalERH.jl")
include("HybridModel.jl")
include("FluidModel.jl")

# Phase 3 — Quantum Simulation
include("QuantumSimulator.jl")
include("QuantumWalk.jl")

version() = v"0.1.0"

end # module ERH
