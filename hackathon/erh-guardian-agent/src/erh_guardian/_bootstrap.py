"""Make the ERH engine importable when running from the Ethic-Latex monorepo.

The guardian depends on the pre-existing ``erh_engine`` package (disclosed).
When it is not installed as a distribution, fall back to the repository root
four levels up (hackathon/erh-guardian-agent/src/erh_guardian -> repo root).
"""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_erh_engine() -> None:
    try:
        import erh_engine  # noqa: F401
        return
    except ImportError:
        pass
    repo_root = Path(__file__).resolve().parents[4]
    if (repo_root / "erh_engine" / "engine.py").exists():
        sys.path.insert(0, str(repo_root))
    import erh_engine  # noqa: F401  # raises if still unavailable
