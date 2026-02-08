#!/usr/bin/env python3
"""
Fetch empirical data for ERH validation in CI pipeline.

Sources:
1. HuggingFace: social_i_qa, moral_stories → J_ij, V(a), error rate E(x)
2. Reddit r/AmItheAsshole (AITA): Firecrawl → crowd V(a)
3. GitHub PR: merge/reject → moral signal for developer network

Usage:
  python scripts/fetch_empirical_erh_data.py [--output-dir data/empirical] [--max-samples 50]
  Set FIRECRAWL_API_KEY for AITA live scrape; GITHUB_TOKEN for PR data.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _fetch_huggingface(output_dir: Path, max_samples: int) -> dict:
    """Load HuggingFace datasets (social_i_qa, moral_stories)."""
    out = {"source": "huggingface", "datasets": {}, "error": None}
    try:
        from simulation.real_data.huggingface_loader import (
            load_social_i_qa,
            load_moral_stories,
            load_and_build_J,
        )
    except ImportError as e:
        out["error"] = str(e)
        return out

    for name, loader in [
        ("social_i_qa", lambda: load_social_i_qa(max_samples=max_samples)),
        ("moral_stories", lambda: load_moral_stories(max_samples=max_samples)),
    ]:
        try:
            rows = loader()
            out["datasets"][name] = {"count": len(rows), "sample": rows[:3] if rows else []}
        except Exception as e:
            out["datasets"][name] = {"error": str(e)}

    # Build J matrix if possible (uses ethics_commonsense by default)
    try:
        J, V = load_and_build_J(max_samples=max_samples, dataset="ethics_commonsense")
        out["J_matrix"] = {
            "shape": list(J.shape) if hasattr(J, "shape") else [],
            "V_shape": list(V.shape) if V is not None and hasattr(V, "shape") else None,
        }
    except Exception as e:
        out["J_matrix"] = {"error": str(e)}

    out_path = output_dir / "huggingface_empirical.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    return out


def _fetch_aita(output_dir: Path, limit: int, use_firecrawl: bool) -> dict:
    """Load AITA-style data (Firecrawl or stub)."""
    out = {"source": "aita", "use_firecrawl": use_firecrawl, "rows": [], "error": None}
    try:
        from simulation.real_data.aita_loader import load_aita_empirical
    except ImportError as e:
        out["error"] = str(e)
        return out

    try:
        rows = load_aita_empirical(limit=limit, use_firecrawl=use_firecrawl)
        out["rows"] = rows[:10]  # Save sample
        out["count"] = len(rows)
    except Exception as e:
        out["error"] = str(e)

    out_path = output_dir / "aita_empirical.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    return out


def _fetch_github_pr(output_dir: Path, repo: str, limit: int) -> dict:
    """Load GitHub PR merge/reject decisions."""
    out = {"source": "github_pr", "repo": repo, "rows": [], "error": None}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        out["error"] = "GITHUB_TOKEN or GH_TOKEN not set"
        out_path = output_dir / "github_pr_empirical.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2, default=str)
        return out

    try:
        from simulation.real_data.github_pr_loader import load_pr_decisions
        rows = load_pr_decisions(repo=repo, token=token, limit=limit)
        out["rows"] = rows[:10]
        out["count"] = len(rows)
    except ImportError as e:
        out["error"] = str(e)
    except Exception as e:
        out["error"] = str(e)

    out_path = output_dir / "github_pr_empirical.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch empirical ERH data for pipeline")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/empirical"),
        help="Output directory for JSON artifacts",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=50,
        help="Max samples per HuggingFace dataset",
    )
    parser.add_argument(
        "--aita-limit",
        type=int,
        default=20,
        help="Limit for AITA posts",
    )
    parser.add_argument(
        "--pr-limit",
        type=int,
        default=30,
        help="Limit for GitHub PRs",
    )
    parser.add_argument(
        "--repo",
        type=str,
        default="dennislee928/Ethic-Latex",
        help="GitHub repo for PR analysis",
    )
    parser.add_argument(
        "--skip-aita",
        action="store_true",
        help="Skip AITA fetch (e.g. when no Firecrawl key)",
    )
    parser.add_argument(
        "--skip-github",
        action="store_true",
        help="Skip GitHub PR fetch",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    use_firecrawl = bool(os.environ.get("FIRECRAWL_API_KEY")) and not args.skip_aita

    print("Fetching HuggingFace (social_i_qa, moral_stories)...")
    hf = _fetch_huggingface(output_dir, args.max_samples)
    print(f"  HuggingFace: {len(hf.get('datasets', {}))} datasets, J_matrix: {hf.get('J_matrix', {})}")

    if not args.skip_aita:
        print("Fetching AITA (Firecrawl or stub)...")
        aita = _fetch_aita(output_dir, args.aita_limit, use_firecrawl)
        print(f"  AITA: {aita.get('count', 0)} rows, firecrawl={use_firecrawl}")
    else:
        print("Skipping AITA (--skip-aita)")

    if not args.skip_github:
        print("Fetching GitHub PR...")
        pr = _fetch_github_pr(output_dir, args.repo, args.pr_limit)
        print(f"  GitHub PR: {pr.get('count', 0)} rows, error={pr.get('error')}")
    else:
        print("Skipping GitHub PR (--skip-github)")

    print(f"Output written to {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
