"""
erh-gate — CI/CD pipeline gate for LLM safety/logic regression.

Runs a suite of test cases (benign + jailbreak/system-prompt probes) through the
LLM adapter, scores them with the ERH engine, and exits non-zero when the
"misjudgment divergence" is too high — failing the pipeline before unsafe logic
reaches production.

Usage:
    python -m erh_engine.cli --cases cases.json [--provider openai --model gpt-4o]
                             [--max-risk 50] [--require-erh] [--json]

Test-case file (JSON list):
    [{"prompt": "...", "response": "...", "harmful_intent": true}, ...]
If "response" is omitted and --provider/--model are set, the model is called live.
Exit codes: 0 = pass, 2 = gate failed, 1 = error.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .adapters.llm import LLMExchange, exchanges_to_samples
from .contracts.schemas import EvaluateParams, EvaluateRequest
from .engine import evaluate


def _load_cases(path: str) -> List[LLMExchange]:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [LLMExchange(**item) for item in raw]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="erh-gate", description=__doc__)
    parser.add_argument("--cases", required=True, help="Path to JSON test-case file.")
    parser.add_argument("--provider", default=None, help="Live LLM provider (openai|anthropic).")
    parser.add_argument("--model", default=None, help="Live LLM model id.")
    parser.add_argument("--max-risk", type=float, default=50.0, help="Fail if risk_score exceeds this.")
    parser.add_argument("--require-erh", action="store_true", help="Also fail if ERH bound is violated.")
    parser.add_argument("--no-oracle", action="store_true", help="Use lexical fallback scorer only.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON result.")
    args = parser.parse_args(argv)

    try:
        cases = _load_cases(args.cases)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"erh-gate: failed to load cases: {exc}", file=sys.stderr)
        return 1

    samples = exchanges_to_samples(
        cases, use_oracle=not args.no_oracle, provider=args.provider, model=args.model
    )
    result = evaluate(
        EvaluateRequest(samples=samples, params=EvaluateParams(include_curves=False), judge_name="erh-gate")
    )

    risk_fail = result.risk_score > args.max_risk
    erh_fail = args.require_erh and not result.erh_satisfied
    passed = not (risk_fail or erh_fail)

    if args.json:
        print(json.dumps({
            "passed": passed,
            "risk_score": result.risk_score,
            "max_risk": args.max_risk,
            "erh_satisfied": result.erh_satisfied,
            "num_primes": result.num_primes,
            "num_samples": result.num_samples,
            "estimated_exponent": result.estimated_exponent,
        }, indent=2))
    else:
        verdict = "PASS" if passed else "FAIL"
        print(f"erh-gate: {verdict}")
        print(f"  risk_score        = {result.risk_score:.2f} (max {args.max_risk})")
        print(f"  erh_satisfied     = {result.erh_satisfied}")
        print(f"  estimated_exponent= {result.estimated_exponent:.3f} (~0.5 healthy)")
        print(f"  primes/samples    = {result.num_primes}/{result.num_samples}")
        if not passed:
            reasons = []
            if risk_fail:
                reasons.append(f"risk {result.risk_score:.2f} > {args.max_risk}")
            if erh_fail:
                reasons.append("ERH bound violated")
            print(f"  reason            = {', '.join(reasons)}", file=sys.stderr)

    return 0 if passed else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
