#!/usr/bin/env python3
"""
LLM Stress Test for ERH Framework (Phase 1.1)

Uses erh to generate moral scenarios (ETHICS-style structure) and calls
OpenAI or Anthropic API to obtain judgments. Computes Π(x), E(x) and
optionally generates charts for paper updates.

Usage:
  Set OPENAI_API_KEY or ANTHROPIC_API_KEY, then:
  python scripts/llm_stress_test.py --provider openai --num-actions 1000
  python scripts/llm_stress_test.py --provider anthropic --num-actions 1000 --output-dir results
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

# ERH package (erh, not simulation)
from erh.core.action_space import generate_world
from erh.core.scenario_generator import actions_to_prompts
from erh.core.ethical_primes import (
    select_ethical_primes,
    compute_Pi_and_error,
    analyze_error_growth,
)

# Optional: chart generation
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# ---- API helpers (requests only, no extra deps) ----

def _parse_judgment_from_text(text: str) -> float | None:
    """Extract a single number in [-1, 1] from model output."""
    if not text or not text.strip():
        return None
    text = text.strip()
    # First try: number on its own line or at start
    patterns = [
        r"^[-+]?\d*\.?\d+\s*$",
        r"^[-+]?\d*\.?\d+",
        r"[-+]?\d*\.?\d+",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.MULTILINE)
        if m:
            try:
                v = float(m.group().strip())
                return float(np.clip(v, -1.0, 1.0))
            except ValueError:
                continue
    return None


def call_openai(user_content: str, system_prompt: str, model: str, api_key: str) -> float | None:
    """Call OpenAI Chat Completions; return parsed J in [-1,1] or None."""
    import requests
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 64,
        "temperature": 0.3,
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        return _parse_judgment_from_text(content)
    except Exception:
        return None


def call_anthropic(user_content: str, system_prompt: str, model: str, api_key: str) -> float | None:
    """Call Anthropic Messages API; return parsed J in [-1,1] or None."""
    import requests
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 64,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_content}],
        "temperature": 0.3,
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        content = ""
        for block in (data.get("content") or []):
            if block.get("type") == "text":
                content += block.get("text", "")
        return _parse_judgment_from_text(content)
    except Exception:
        return None


def get_judgment_from_llm(
    user_content: str,
    system_prompt: str,
    provider: str,
    model: str,
    api_key: str,
) -> float | None:
    if provider == "openai":
        return call_openai(user_content, system_prompt, model, api_key)
    if provider == "anthropic":
        return call_anthropic(user_content, system_prompt, model, api_key)
    return None


# ---- Main pipeline ----

def run_stress_test(
    num_actions: int = 10_000,
    complexity_dist: str = "zipf",
    complexity_range: tuple = (1, 100),
    provider: str = "openai",
    model: str | None = None,
    api_key: str | None = None,
    tau: float = 0.3,
    random_seed: int | None = 42,
    scenario_template: str = "minimal",
    delay_seconds: float = 0.0,
    output_dir: str | None = None,
    save_actions_json: bool = True,
    generate_charts: bool = True,
    X_max: int = 100,
) -> dict:
    """
    Generate scenarios, call LLM for each, compute Π/E and optionally charts.

    Returns
    -------
    dict with keys: config, actions_summary, metrics, analysis, output_paths
    """
    if provider == "openai":
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        model = model or "gpt-4o-mini"
    else:
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        model = model or "claude-3-5-haiku-20241022"

    if not api_key:
        raise ValueError(
            f"Set {provider.upper()}_API_KEY or pass --api-key. "
            "No API key found."
        )

    out_dir = Path(output_dir or "llm_stress_test_results")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate world (ETHICS-style: many scenarios, varying complexity)
    print(f"Generating {num_actions} scenarios (dist={complexity_dist}, seed={random_seed})...")
    actions = generate_world(
        num_actions=num_actions,
        complexity_dist=complexity_dist,
        complexity_range=complexity_range,
        random_seed=random_seed,
    )
    prompts = actions_to_prompts(actions, template=scenario_template)

    # 2. Call LLM for each scenario
    print(f"Calling {provider} ({model}) for {len(prompts)} scenarios...")
    failed = 0
    for i, item in enumerate(prompts):
        J = get_judgment_from_llm(
            item["user_content"],
            item["system_prompt"],
            provider=provider,
            model=model,
            api_key=api_key,
        )
        action = item["action"]
        if J is not None:
            action.J = J
            action.delta = J - action.V
            action.mistake_flag = 1 if abs(action.delta) > tau else 0
        else:
            action.J = None
            action.delta = None
            action.mistake_flag = 0
            failed += 1
        if delay_seconds > 0:
            time.sleep(delay_seconds)
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{len(prompts)} done, {failed} parse failures")

    # 3. Summary and Π/E analysis
    judged = [a for a in actions if a.J is not None]
    mistakes = sum(1 for a in judged if a.mistake_flag == 1)
    primes = select_ethical_primes(judged, importance_quantile=0.9)
    Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=X_max)
    analysis = analyze_error_growth(E_x, x_vals)

    metrics = {
        "total_actions": num_actions,
        "judged": len(judged),
        "parse_failures": failed,
        "mistakes_count": mistakes,
        "mistake_rate": mistakes / len(judged) if judged else 0,
        "ethical_primes_count": len(primes),
        "erh_satisfied": bool(analysis.get("erh_satisfied", False)),
        "estimated_exponent": analysis.get("estimated_exponent"),
        "alpha_ci_low": analysis.get("alpha_ci_low"),
        "alpha_ci_high": analysis.get("alpha_ci_high"),
    }

    result = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "num_actions": num_actions,
            "complexity_dist": complexity_dist,
            "complexity_range": list(complexity_range),
            "provider": provider,
            "model": model,
            "tau": tau,
            "random_seed": random_seed,
            "scenario_template": scenario_template,
        },
        "metrics": metrics,
        "analysis": {k: v for k, v in analysis.items() if isinstance(v, (int, float, bool, str))},
    }

    output_paths = []

    # 4. Save lightweight results (no full action list by default to keep file small)
    summary_path = out_dir / "llm_stress_test_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    output_paths.append(str(summary_path))

    if save_actions_json:
        # Save compact action results for reproducibility
        actions_data = [
            {
                "id": a.id,
                "c": a.c,
                "V": round(a.V, 4),
                "w": round(a.w, 4),
                "J": round(a.J, 4) if a.J is not None else None,
                "delta": round(a.delta, 4) if a.delta is not None else None,
                "mistake_flag": a.mistake_flag,
            }
            for a in actions
        ]
        actions_path = out_dir / "llm_stress_test_actions.json"
        with open(actions_path, "w", encoding="utf-8") as f:
            json.dump(actions_data, f, indent=0, ensure_ascii=False)
        output_paths.append(str(actions_path))

    # 5. Charts (Π(x), E(x)) for paper update
    if generate_charts and HAS_MATPLOTLIB:
        _, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        axes[0].plot(x_vals, Pi_x, label=r"$\Pi(x)$", color="C0")
        axes[0].plot(x_vals, B_x, label=r"$B(x)$", color="C1", linestyle="--")
        axes[0].set_ylabel("Count")
        axes[0].legend()
        axes[0].set_title("Ethical prime count vs baseline")
        axes[0].grid(True, alpha=0.3)

        axes[1].plot(x_vals, E_x, label=r"$E(x) = \Pi(x) - B(x)$", color="C2")
        axes[1].axhline(0, color="gray", linestyle="-", alpha=0.5)
        axes[1].set_xlabel("Complexity x")
        axes[1].set_ylabel("Error E(x)")
        axes[1].legend()
        axes[1].set_title("ERH error term")
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        chart_path = out_dir / "llm_stress_test_Pi_E.png"
        plt.savefig(chart_path, dpi=150)
        plt.close()
        output_paths.append(str(chart_path))

    result["output_paths"] = output_paths
    print(f"Done. Summary: {summary_path}")
    print(f"  Mistake rate: {metrics['mistake_rate']:.4f}, ERH satisfied: {metrics['erh_satisfied']}")
    return result


def _run_dry_run(args):
    """Generate scenarios and save prompts to JSON; no API calls."""
    actions = generate_world(
        num_actions=args.num_actions,
        complexity_dist=args.complexity_dist,
        random_seed=args.seed,
    )
    prompts = actions_to_prompts(actions, template=args.scenario_template)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sample = [
        {"action_id": p["action_id"], "user_content": p["user_content"][:200]}
        for p in prompts[:5]
    ]
    path = out_dir / "llm_stress_test_dry_run_prompts_sample.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"num_prompts": len(prompts), "sample": sample}, f, indent=2, ensure_ascii=False)
    print(f"Dry run: generated {len(prompts)} prompts. Sample saved to {path}")


def main():
    parser = argparse.ArgumentParser(
        description="LLM stress test for ERH: generate scenarios, call OpenAI/Anthropic, compute Π/E."
    )
    parser.add_argument("--num-actions", type=int, default=10_000, help="Number of scenarios (default 10000)")
    parser.add_argument(
        "--complexity-dist",
        type=str,
        default="zipf",
        choices=["zipf", "uniform", "power_law"],
        help="Complexity distribution",
    )
    parser.add_argument("--provider", type=str, default="openai", choices=["openai", "anthropic"])
    parser.add_argument("--model", type=str, default=None, help="Model name (default: gpt-4o-mini / claude-3-5-haiku)")
    parser.add_argument("--api-key", type=str, default=None, help="API key (else from env OPENAI_API_KEY / ANTHROPIC_API_KEY)")
    parser.add_argument("--tau", type=float, default=0.3, help="Mistake threshold |Δ| > τ")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--scenario-template", type=str, default="minimal", choices=["minimal", "narrative"])
    parser.add_argument("--delay", type=float, default=0.0, help="Seconds between API calls (rate limit)")
    parser.add_argument("--output-dir", type=str, default="llm_stress_test_results")
    parser.add_argument("--no-actions-json", action="store_true", help="Do not save full actions JSON")
    parser.add_argument("--no-charts", action="store_true", help="Do not generate Π/E charts")
    parser.add_argument("--X-max", type=int, default=100, help="Max complexity for Π/E")
    parser.add_argument("--dry-run", action="store_true", help="Only generate scenarios and save prompts; no API calls")
    args = parser.parse_args()

    if args.dry_run:
        _run_dry_run(args)
        return

    try:
        run_stress_test(
            num_actions=args.num_actions,
            complexity_dist=args.complexity_dist,
            provider=args.provider,
            model=args.model,
            api_key=args.api_key,
            tau=args.tau,
            random_seed=args.seed,
            scenario_template=args.scenario_template,
            delay_seconds=args.delay,
            output_dir=args.output_dir,
            save_actions_json=not args.no_actions_json,
            generate_charts=not args.no_charts,
            X_max=args.X_max,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
