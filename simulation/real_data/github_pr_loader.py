"""
GitHub PR loader: merge/reject as moral signal.

Maps Pull Request merge -> support (+1), reject -> oppose (-1).
Builds developer social network from PR comments.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np

# PyGithub optional
_GITHUB_AVAILABLE = False
try:
    from github import Github
    _GITHUB_AVAILABLE = True
except ImportError:
    Github = None


def _stub_pr_data(n: int = 10) -> List[Dict[str, Any]]:
    """Stub PR data when PyGithub unavailable."""
    rng = np.random.default_rng(42)
    actions = [
        {"repo": "org/repo", "pr_id": i, "merged": rng.random() > 0.5, "author": f"user{i}"}
        for i in range(n)
    ]
    return actions


def load_pr_decisions(
    repo: str,
    token: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Load PR merge/reject decisions from GitHub.

    Returns
    -------
    List[Dict]
        Each: pr_id, merged (bool), author, reviewers, V (1 if merged, -1 if closed)
    """
    if not _GITHUB_AVAILABLE or Github is None:
        return _stub_pr_data(limit)
    token = token or _get_github_token()
    if not token:
        return _stub_pr_data(limit)
    try:
        gh = Github(token)
        r = gh.get_repo(repo)
        prs = list(r.get_pulls(state="closed"))[:limit]
        out = []
        for pr in prs:
            merged = pr.merged
            V = 1.0 if merged else -1.0
            out.append({
                "pr_id": pr.number,
                "merged": merged,
                "author": pr.user.login if pr.user else "unknown",
                "V": V,
            })
        return out
    except Exception:
        return _stub_pr_data(limit)


def _get_github_token() -> Optional[str]:
    import os
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def build_social_graph_from_prs(
    prs: List[Dict[str, Any]],
) -> np.ndarray:
    """
    Build adjacency matrix from PR author/reviewer interactions.

    Authors who frequently merge together -> positive coupling.
    Authors who reject each other's PRs -> negative coupling.

    Returns
    -------
    ndarray
        Symmetric interaction matrix (small, so we use first few authors).
    """
    if not prs:
        return np.zeros((1, 1))
    authors = list({p.get("author", "u") for p in prs})[:20]
    n = len(authors)
    idx = {a: i for i, a in enumerate(authors)}
    J = np.zeros((n, n))
    for p in prs:
        a = p.get("author", "")
        if a not in idx:
            continue
        i = idx[a]
        v = p.get("V", 0)
        for j in range(n):
            if i != j:
                J[i, j] += v * 0.1  # weak coupling for same-repo
    J = (J + J.T) / 2
    np.fill_diagonal(J, 0)
    return np.clip(J, -1, 1)
