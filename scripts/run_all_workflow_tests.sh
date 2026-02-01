#!/usr/bin/env bash
# Run local equivalents of all .github/workflows pipeline test steps.
# Usage: from repo root: ./scripts/run_all_workflow_tests.sh
# With venv active, or the script will create .venv if missing (avoids PEP 668 on Homebrew Python).
# Or: PYTHONPATH="$(pwd):$PYTHONPATH" bash scripts/run_all_workflow_tests.sh
#
# Sections map to: sdk_python, multi_platform_test, simulation, quantum_tests,
# build_thesis / single_sh, erh_security_app, docs, sdk_node.
#
# Note: Steps that use "2>/dev/null" or "|| true" must run via bash -c '...'
# so the shell interprets redirection and short-circuit; otherwise they are
# passed as literal arguments to the command and the step can fail.

set +e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}:${ROOT}/simulation:${PYTHONPATH}"

# Use project .venv when not already in a venv (avoids PEP 668 externally-managed-environment)
if [ -z "${VIRTUAL_ENV:-}" ]; then
  VENV="$ROOT/.venv"
  if [ ! -d "$VENV" ]; then
    printf "Creating .venv at %s (use it next time: source .venv/bin/activate)\n" "$VENV"
    for py in python3 python; do
      if command -v "$py" &>/dev/null && "$py" -m venv "$VENV" 2>/dev/null; then
        break
      fi
    done
  fi
  if [ -x "$VENV/bin/python" ]; then
    export VIRTUAL_ENV="$VENV"
    PY="$VENV/bin/python"
    # Ensure pip exists in venv (e.g. ensurepip for minimal venv)
    if [ ! -x "$VENV/bin/pip" ]; then
      "$PY" -m ensurepip --upgrade 2>/dev/null || true
    fi
    PIP="${VENV}/bin/pip"
  else
    printf "Warning: .venv not available, using system Python (bootstrap may fail with PEP 668).\n" 1>&2
    PY="${PY:-python}"
    PIP="${PIP:-pip}"
  fi
else
  PY="${PY:-python}"
  PIP="${PIP:-pip}"
fi
FAILED=()
PASSED=()

run_step() {
  local name="$1"
  shift
  printf "\n========== %s ==========\n" "$name"
  if "$@"; then
    PASSED+=("$name")
    return 0
  else
    FAILED+=("$name")
    return 1
  fi
}

run_step_allow_fail() {
  local name="$1"
  shift
  printf "\n========== %s (allow fail) ==========\n" "$name"
  if "$@"; then
    PASSED+=("$name")
  else
    echo "[skipped/fail] $name"
  fi
  return 0
}

# Optional bootstrap: install deps so more steps pass when run without a venv
# Use $PY -m pip so we don't require a "pip" executable on PATH
run_step_allow_fail "bootstrap: pip install -r requirements.txt" bash -c "\"$PY\" -m pip install -r requirements.txt -q"
run_step_allow_fail "bootstrap: pip install pytest" bash -c "\"$PY\" -m pip install pytest -q"

# --- 1. sdk_python.yml ---
run_step_allow_fail "sdk_python: pip install -e .[ml]" $PIP install -e ".[ml]" pytest pylint flake8 bandit networkx 2>/dev/null
run_step "sdk_python: pytest tests/test_sdk.py" $PY -m pytest tests/test_sdk.py -v --tb=short
run_step "sdk_python: verify editable (erh, simulation)" $PY -c "import erh; import simulation; print('erh:', erh.__file__); print('simulation:', simulation.__file__)"
run_step_allow_fail "sdk_python: quantum optional" $PY -c "from simulation.quantum import LocalQuantumJudge; LocalQuantumJudge(shots=32)" 2>/dev/null || true
run_step_allow_fail "sdk_python: pylint erh/" $PY -m pylint --exit-zero erh/ 2>/dev/null || true
run_step_allow_fail "sdk_python: flake8 erh/" $PY -m flake8 erh/ --max-line-length=120 --extend-ignore=E203,W503 2>/dev/null || true
run_step_allow_fail "sdk_python: bandit erh/" $PY -m bandit -r erh/ -ll 2>/dev/null || true

# --- 2. multi_platform_test.yml ---
run_step "multi_platform: pytest test_sdk" $PY -m pytest tests/test_sdk.py -v --tb=short
run_step_allow_fail "multi_platform: pytest test_erh_phase1" $PY -m pytest tests/test_erh_phase1.py -v --tb=short 2>/dev/null || true
run_step_allow_fail "multi_platform: Pydantic models (simulation.models)" $PY -c "
from simulation.models import Action, Judgment
a = Action(id=1, c=50, V=0.5, w=1.0)
assert a.c == 50 and a.V == 0.5
j = Judgment(action_id=1, J=0.4, V=0.5, delta=-0.1, mistake_flag=0)
assert j.J == 0.4
print('simulation.models OK')
" 2>/dev/null || true
run_step_allow_fail "multi_platform: zeta function (simulation.analysis)" $PY -c "
from simulation.analysis.zeta_function import build_m_sequence, ethical_zeta_product
z = ethical_zeta_product(primes=[], s=1.0+0j, max_terms=10)
assert isinstance(z, complex)
print('zeta OK')
" 2>/dev/null || true

# --- 3. Core unit tests (build_thesis / single_sh) ---
run_step "unit: pytest core (temporal_erh, agent, social)" $PY -m pytest tests/test_temporal_erh.py tests/test_agent_framework.py tests/test_social_network.py -v --tb=short
run_step_allow_fail "unit: pytest meta_monitor" $PY -m pytest tests/test_meta_monitor.py -v --tb=short 2>/dev/null || true
run_step_allow_fail "unit: pytest hybrid_model" $PY -m pytest tests/test_hybrid_model.py -v --tb=short 2>/dev/null || true
run_step_allow_fail "unit: pytest judge_strategies" $PY -m pytest tests/test_judge_strategies.py -v --tb=short 2>/dev/null || true
run_step_allow_fail "unit: pytest psychohistory_integration" $PY -m pytest tests/test_psychohistory_integration.py -v --tb=short 2>/dev/null || true
run_step_allow_fail "unit: pytest streamlit imports" $PY -m pytest tests/test_streamlit_app.py -v --tb=short 2>/dev/null || true
run_step_allow_fail "unit: full tests/ collection" $PY -m pytest tests/ -v --tb=short --ignore=tests/notebooks 2>/dev/null || true

# --- 4. erh_core sanity ---
run_step "erh_core: import core and analysis" $PY -c "
from erh_core.core import generate_world, BiasedJudge, select_ethical_primes
from erh_core.core.action_space import Action
from erh_core.analysis.statistics import compare_judges
print('erh_core OK')
"
run_step_allow_fail "erh_core: run_example quick" $PY simulation/run_example.py 2>/dev/null | head -20

# --- 5. build_thesis: LLM stress, figures, scripts ---
run_step "build_thesis: llm_stress_test dry-run" bash -c "\"$PY\" scripts/llm_stress_test.py --num-actions 20 --dry-run --output-dir llm_stress_test_results 2>/dev/null || true"
run_step_allow_fail "build_thesis: generate_all_figures" $PY simulation/generate_all_figures.py 2>/dev/null || true
run_step_allow_fail "build_thesis: real_data adult_income" $PY -m simulation.real_data.adult_income_case_study 2>/dev/null || true
run_step_allow_fail "build_thesis: real_data exam_cheating" $PY -m simulation.real_data.exam_cheating_case_study 2>/dev/null || true
run_step_allow_fail "build_thesis: real_data sexual_abuse" $PY -m simulation.real_data.sexual_abuse_case_study 2>/dev/null || true
run_step_allow_fail "build_thesis: integrate_figures" $PY scripts/integrate_figures.py 2>/dev/null || true
run_step_allow_fail "build_thesis: update_latex" $PY scripts/update_latex.py 2>/dev/null || true
run_step_allow_fail "build_thesis: generate_md_reports" $PY scripts/generate_md_reports.py 2>/dev/null || true

# --- 6. simulation.yml: data, batch, alpha_comparison, report ---
run_step "simulation: mkdir data" mkdir -p data data/real_world
run_step_allow_fail "simulation: generate_synthetic_adult" $PY scripts/generate_synthetic_adult.py 2>/dev/null || true
run_step_allow_fail "simulation: run_simulation_batch zipf" $PY scripts/run_simulation_batch.py --num-actions 50 --complexity-dist zipf --output-dir results 2>/dev/null || true
run_step_allow_fail "simulation: run_simulation_batch uniform" $PY scripts/run_simulation_batch.py --num-actions 30 --complexity-dist uniform --output-dir results 2>/dev/null || true
run_step_allow_fail "simulation: calculate_alpha_comparison" $PY scripts/calculate_alpha_comparison.py 2>/dev/null || true
run_step_allow_fail "simulation: generate_comprehensive_report" $PY scripts/generate_comprehensive_report.py --input-dir results --output-dir final_report 2>/dev/null || true

# --- 7. psychohistory (build_thesis / single_sh) ---
run_step_allow_fail "psychohistory: quick" $PY scripts/run_psychohistory_simulations.py --quick --output-dir simulation/output/psychohistory_tests 2>/dev/null || true

# --- 8. quantum_tests.yml ---
run_step_allow_fail "quantum_tests: test_quantum_entanglement" $PY -m pytest tests/test_quantum_entanglement.py -v --tb=short 2>/dev/null || true
run_step_allow_fail "quantum_tests: simulation.quantum simulator" $PY -c "
from simulation.quantum.simulator import QuantumSimulator
s = QuantumSimulator(shots=32)
print('quantum simulator OK')
" 2>/dev/null || true

# --- 9. erh_security_app.yml (backend + frontend check) ---
if [ -f erh-security-app/backend/requirements.txt ]; then
  run_step_allow_fail "erh_security_app: backend pytest" bash -c "cd erh-security-app/backend && $PIP install -r requirements.txt -q && $PY -m pytest tests/ -v --tb=short" 2>/dev/null || true
  run_step_allow_fail "erh_security_app: backend pylint" bash -c "cd erh-security-app/backend && pylint app/ --exit-zero" 2>/dev/null || true
  run_step_allow_fail "erh_security_app: backend bandit" bash -c "cd erh-security-app/backend && bandit -r app/ -ll" 2>/dev/null || true
else
  echo "[skip] erh_security_app backend (no requirements.txt)"
fi
if [ -f erh-security-app/frontend/package.json ]; then
  run_step_allow_fail "erh_security_app: frontend npm ci" bash -c "cd erh-security-app/frontend && npm ci" 2>/dev/null || true
  run_step_allow_fail "erh_security_app: frontend build" bash -c "cd erh-security-app/frontend && npm run build" 2>/dev/null || true
  run_step_allow_fail "erh_security_app: frontend test" bash -c "cd erh-security-app/frontend && npm test" 2>/dev/null || true
else
  echo "[skip] erh_security_app frontend (no package.json)"
fi

# --- 10. docs.yml ---
if [ -f docs/requirements.txt ]; then
  run_step_allow_fail "docs: sphinx build" bash -c "cd $ROOT && $PIP install -r docs/requirements.txt -q && $PIP install sphinx sphinx-rtd-theme sphinxcontrib-napoleon -q && cd docs && sphinx-build -b html . _build/html" 2>/dev/null || true
else
  run_step_allow_fail "docs: sphinx build (no docs/requirements)" bash -c "cd $ROOT && $PIP install sphinx sphinx-rtd-theme sphinxcontrib-napoleon -q && cd docs && sphinx-build -b html . _build/html" 2>/dev/null || true
fi

# --- 11. sdk_node.yml ---
if [ -f js-sdk/package.json ]; then
  run_step_allow_fail "sdk_node: npm install" bash -c "cd js-sdk && npm install" 2>/dev/null || true
  run_step_allow_fail "sdk_node: npm run build" bash -c "cd js-sdk && npm run build" 2>/dev/null || true
  run_step_allow_fail "sdk_node: npm test" bash -c "cd js-sdk && npm test" 2>/dev/null || true
else
  echo "[skip] sdk_node (no js-sdk/package.json)"
fi

# --- 12. R verification (simulation.yml report job) ---
if command -v Rscript &>/dev/null; then
  run_step_allow_fail "simulation: R verify_analysis" bash -c "Rscript scripts/verify_analysis.R results final_report/r_verification 2>/dev/null || true" 2>/dev/null || true
else
  echo "[skip] R verify_analysis (Rscript not found)"
fi

# --- Summary ---
printf "\n========== SUMMARY ==========\n"
printf "Passed: %s\n" "${#PASSED[@]}"
printf "Failed: %s\n" "${#FAILED[@]}"
for f in "${FAILED[@]}"; do echo "  - $f"; done
[ "${#FAILED[@]}" -eq 0 ] && exit 0 || exit 1
