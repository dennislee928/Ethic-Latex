  Workflow: julia_tests.yml
  Changed?: Already correct (created fresh)            
  What was updated: —
  ────────────────────────────────────────
  Workflow: quantum_tests.yml
  Changed?: Updated
  What was updated: Added julia/src/Quantum*.jl + julia/test/test_quantum_*.jl to paths triggers; added julia-quantum job running Yao.jl tests (continue-on-error: true)
  ────────────────────────────────────────
  Workflow: simulation.yml
  Changed?: Updated
  What was updated: Added julia-simulate job (runs run_simulation_batch.jl --smoke + run_phase_transition.jl --smoke); added it to report job's needs list
  ────────────────────────────────────────
  Workflow: sdk_python.yml
  Changed?: Updated
  What was updated: Added Julia setup + PyJulia bridge step that verifies the _zeta_pure.py fallback always works regardless of Julia availability (continue-on-error: true)
  ────────────────────────────────────────
  Workflow: multi_platform_test.yml
  Changed?: Updated
  What was updated: Added conditional Julia package smoke test on ubuntu-latest only — installs Julia, instantiates project, verifies EthicalPrimes.jl loads (continue-on-error: true)
  ────────────────────────────────────────
  Workflow: erh_security_app.yml
  Changed?: No change
  What was updated: FastAPI/Next.js untouched
  ────────────────────────────────────────
  Workflow: docs.yml
  Changed?: No change
  What was updated: Sphinx build untouched
  ────────────────────────────────────────
  Workflow: build_thesis*.yml
  Changed?: No change
  What was updated: LaTeX untouched
  ────────────────────────────────────────
  Workflow: repo_smoke.yml
  Changed?: No change
  What was updated: Imports simulation.analysis.zeta_function (not erh_core) — unaffected by shim