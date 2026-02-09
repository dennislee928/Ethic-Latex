#!/usr/bin/env python3
"""
Check for placeholder strings in .tex files before committing.

Fails (exit 1) if any of [To be filled], [Insert Data], [Pending] are found.
Use as pre-commit hook or in CI.

Usage:
    python scripts/check_tex_placeholders.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PLACEHOLDERS = ["[To be filled]", "[Insert Data]", "[Pending]", "[TBD]"]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    found = []
    for path in PROJECT_ROOT.rglob("*.tex"):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            for ph in PLACEHOLDERS:
                if ph in text:
                    found.append((path, ph))
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
