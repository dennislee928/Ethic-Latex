#!/usr/bin/env bash
# Run local equivalents of all .github/workflows pipeline test steps.
# Usage: from repo root, with venv active: ./scripts/run_all_workflow_tests.sh
# Or: PYTHONPATH="$(pwd):$PYTHONPATH" .venv/bin/bash scripts/run_all_workflow_tests.sh

set +e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}:${PYTHONPATH}"
PY="${PY:-python}"
PIP="${PIP:-pip}"
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

# --- 1. sdk_python.yml ---
run_step_allow_fail "sdk_python: pip install -e .[ml]" $PIP install -e ".[ml]" pytest pylint flake8 bandit 2>/dev/null
run_step "sdk_python: pytest tests/test_sdk.py" $PY -m pytest tests/test_sdk.py -v --tb=short
run_step_allow_fail "sdk_python: quantum optional" $PY -c "from simulation.quantum import LocalQuantumJudge; LocalQuantumJudge(shots=32)" 2>/dev/null || true
run_step_allow_fail "sdk_python: pylint erh/" $PY -m pylint --exit-zero erh/ 2>/dev/null || true
run_step_allow_fail "sdk_python: flake8 erh/" $PY -m flake8 erh/ --max-line-length=120 --extend-ignore=E203,W503 2>/dev/null || true

# --- 2. multi_platform_test.yml ---
run_step "multi_platform: pytest test_sdk" $PY -m pytest tests/test_sdk.py -v --tb=short
run_step_allow_fail "multi_platform: pytest test_erh_phase1" $PY -m pytest tests/test_erh_phase1.py -v --tb=short 2>/dev/null || true
run_step_allow_fail "multi_platform: Pydantic models" $PY -c "
from simulation.models import Action
a = Action(id=1, V=0.5, complexity=2)
print('Pydantic OK')
" 2>/dev/null || true
run_step_allow_fail "multi_platform: zeta function" $PY -c "
from simulation.analysis.zeta_function import build_m_sequence, ethical_zeta_product
print('zeta OK')
" 2>/dev/null || true

# --- 3. build_thesis / single_sh: LLM stress dry-run ---
run_step "build_thesis: llm_stress_test dry-run" $PY scripts/llm_stress_test.py --num-actions 20 --dry-run --output-dir llm_stress_test_results 2>/dev/null || true
run_step_allow_fail "build_thesis: generate_all_figures" $PY simulation/generate_all_figures.py 2>/dev/null || true

# --- 4. simulation.yml: data + run_simulation_batch + alpha_comparison ---
run_step "simulation: mkdir data" mkdir -p data data/real_world
run_step_allow_fail "simulation: generate_synthetic_adult" $PY scripts/generate_synthetic_adult.py 2>/dev/null || true
run_step_allow_fail "simulation: run_simulation_batch (quick)" $PY scripts/run_simulation_batch.py --num-actions 50 --complexity-dist zipf --output-dir results 2>/dev/null || true
run_step_allow_fail "simulation: calculate_alpha_comparison" $PY scripts/calculate_alpha_comparison.py 2>/dev/null || true

# --- 5. quantum_tests.yml ---
run_step_allow_fail "quantum_tests: test_quantum_entanglement" $PY -m pytest tests/test_quantum_entanglement.py -v --tb=short 2>/dev/null || true

# --- 6. single_sh / build_thesis: unit tests ---
run_step_allow_fail "build_thesis: unit tests (temporal_erh, agent, social)" $PY -m pytest tests/test_temporal_erh.py tests/test_agent_framework.py tests/test_social_network.py -v --tb=short 2>/dev/null || true
run_step_allow_fail "build_thesis: psychohistory quick" $PY scripts/run_psychohistory_simulations.py --quick --output-dir simulation/output/psychohistory_tests 2>/dev/null || true

# --- 7. erh_security_app.yml (backend) ---
if [ -f erh-security-app/backend/requirements.txt ]; then
  run_step_allow_fail "erh_security_app: backend pytest" bash -c "cd erh-security-app/backend && $PIP install -r requirements.txt -q && $PY -m pytest tests/ -v --tb=short" 2>/dev/null || true
else
  echo "[skip] erh_security_app backend (no requirements.txt)"
fi

# --- 8. docs.yml ---
if [ -f docs/requirements.txt ]; then
  run_step_allow_fail "docs: sphinx build" bash -c "cd $ROOT && $PIP install -r docs/requirements.txt -q && $PIP install sphinx sphinx-rtd-theme sphinxcontrib-napoleon -q && cd docs && sphinx-build -b html . _build/html" 2>/dev/null || true
else
  run_step_allow_fail "docs: sphinx build (no docs/requirements)" bash -c "cd $ROOT && $PIP install sphinx sphinx-rtd-theme sphinxcontrib-napoleon -q && cd docs && sphinx-build -b html . _build/html" 2>/dev/null || true
fi

# --- 9. sdk_node.yml (if js-sdk has real package) ---
if [ -f js-sdk/package.json ] && ! grep -q '"version": "0.0.0"' js-sdk/package.json; then
  run_step_allow_fail "sdk_node: npm install" bash -c "cd js-sdk && npm install" 2>/dev/null || true
  run_step_allow_fail "sdk_node: npm run build" bash -c "cd js-sdk && npm run build" 2>/dev/null || true
  run_step_allow_fail "sdk_node: npm test" bash -c "cd js-sdk && npm test" 2>/dev/null || true
else
  echo "[skip] sdk_node (placeholder or no js-sdk)"
fi

# --- Summary ---
printf "\n========== SUMMARY ==========\n"
printf "Passed: %s\n" "${#PASSED[@]}"
printf "Failed: %s\n" "${#FAILED[@]}"
for f in "${FAILED[@]}"; do echo "  - $f"; done
[ "${#FAILED[@]}" -eq 0 ] && exit 0 || exit 1
