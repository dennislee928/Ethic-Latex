# Changelog

All notable changes to the Ethical Riemann Hypothesis (ERH) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — 2026-05-16

### Added
- Julia package `ERH.jl` at `julia/` — replaces compute-heavy Python components with Julia equivalents
- Phase 1: EthicalPrimes.jl, ZetaFunction.jl, ERHChecks.jl, ERHStatistics.jl (mathematical core)
- Phase 2: ABMSimulator.jl, SocialNetwork.jl, TemporalERH.jl, HybridModel.jl, FluidModel.jl (simulation framework)
- Phase 3: QuantumSimulator.jl, QuantumWalk.jl using Yao.jl (local quantum simulation)
- Phase 4: Julia batch scripts in julia/scripts/ replacing Python equivalents
- GitHub Actions workflow `.github/workflows/julia_tests.yml` for Julia CI
- PyJulia bridge shims for transparent fallback to pure Python

### Changed
- erh_core/analysis/zeta_function.py now delegates to Julia when PyJulia is available, falls back to pure Python

### Implementation details
- `julia/src/server.jl` — HTTP sidecar (port 8080) with 4 simulation modes (abm, temporal, fluid, hybrid); activate with `ERH_JULIA_BACKEND=true`
- `julia/QUANTUM_NOTE.md` — documents which Python quantum files are replaced vs. kept
- `erh_core/analysis/_zeta_pure.py` — pure-Python fallback preserved; `zeta_function.py` now auto-delegates to Julia when PyJulia available
- Total new Julia code: ~6,500 lines across 11 source modules + 11 test files + 6 batch scripts

---

## [Unreleased] (prior)

### Added
- R package installation support in CI/CD workflows
- PNG/JPG figure export from simulation workflow for thesis integration
- Microtype package for enhanced LaTeX typography
- Improved table float placement options ([htbp] instead of [h])

### Changed
- Updated LaTeX table float options from `[h]` to `[htbp]` for better layout flexibility
- R package installation now uses user library path to avoid permission issues

### Fixed
- Fixed R package installation permission errors in CI/CD
- Fixed trailing whitespace in workflow files

## [0.1.0] - 2024-12-18

### Added
- Initial release of ERH SDK
- Core simulation modules (action space, judgment systems, ethical primes)
- Analysis tools (zeta function, error metrics, statistics)
- Visualization modules for paper figures
- Python SDK with local and remote client support
- Jupyter notebook examples
- LaTeX thesis documents (English and Chinese versions)
- CI/CD workflows for testing and building

### Documentation
- README with installation and usage instructions
- API documentation via docstrings
- Project summary and implementation status documents

