#!/usr/bin/env python3
"""Run all three Phase 1 verification steps in one process (avoids repeated startup)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    errors = []
    # 1) Imports and ethical_primality_test
    try:
        from erh.core import ethical_primality_test, actions_to_prompts
        from erh.core.action_space import generate_world
        import numpy as np
        w = generate_world(10, random_seed=42)
        p = actions_to_prompts(w)
        assert len(p) == 10
        E = np.array([0.1, 0.2, 0.5, 0.3, 0.2])
        x = np.array([1, 2, 3, 4, 5])
        assert isinstance(ethical_primality_test(5, E, x), bool)
        print("[1/3] OK: imports and ethical_primality_test")
    except Exception as e:
        errors.append(("imports + ethical_primality_test", e))
        print("[1/3] FAIL:", e)

    # 2) Dry-run
    try:
        from erh.core.action_space import generate_world
        from erh.core.scenario_generator import actions_to_prompts
        actions = generate_world(num_actions=5, random_seed=42)
        prompts = actions_to_prompts(actions, template="minimal")
        out_dir = ROOT / "llm_stress_test_results"
        out_dir.mkdir(parents=True, exist_ok=True)
        import json
        sample = [{"action_id": q["action_id"], "user_content": q["user_content"][:200]} for q in prompts[:3]]
        path = out_dir / "llm_stress_test_dry_run_prompts_sample.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"num_prompts": len(prompts), "sample": sample}, f, indent=2, ensure_ascii=False)
        print("[2/3] OK: dry-run (wrote", path.name + ")")
    except Exception as e:
        errors.append(("dry-run", e))
        print("[2/3] FAIL:", e)

    # 3) Unit tests (run pytest in-process via its API)
    try:
        import pytest
        result = pytest.main(["-v", "--tb=short", str(ROOT / "tests" / "test_erh_phase1.py"), "-x"])
        if result == 0:
            print("[3/3] OK: pytest test_erh_phase1.py passed")
        else:
            errors.append(("pytest", f"exit code {result}"))
    except Exception as e:
        errors.append(("pytest", e))
        print("[3/3] FAIL:", e)

    if errors:
        print("\nErrors:", errors)
        sys.exit(1)
    print("\nAll three verifications passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
