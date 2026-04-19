#!/usr/bin/env python3
"""
Check for placeholder strings in .tex files before committing.

Fails (exit 1) if any of [To be filled], [Insert Data], [Pending] are found.
Use as pre-commit hook or in CI.

Usage:
    python scripts/check_tex_placeholders.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PLACEHOLDERS = ["[To be filled]", "[Insert Data]", "[Pending]", "[TBD]"]
ALL_CAPS_PLACEHOLDER = re.compile(r"\[[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\]")
PROJECT_ROOT = Path(__file__).resolve().parents[1]


SKIP_DIRS = {".git", "node_modules", ".worktrees", ".venv", ".venv_erh", ".venv_new", ".venv_sphinx"}

# Only the production-ready LaTeX sources are checked; draft originals are excluded.
SKIP_FILES = {"ethical_riemann_hypothesis.tex"}


def main() -> int:
    found = []
    for path in PROJECT_ROOT.rglob("*.tex"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            for ph in PLACEHOLDERS:
                if ph in text:
                    found.append((path, ph))
            for match in ALL_CAPS_PLACEHOLDER.finditer(text):
                found.append((path, match.group(0)))
        except Exception:
            pass

    if found:
        print("ERROR: Placeholder strings found in .tex files:")
        for p, ph in found:
            print(f"  {p}: {ph}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
