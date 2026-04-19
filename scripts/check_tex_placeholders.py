#!/usr/bin/env python3
"""
Check thesis .tex files for placeholder strings and stale review regressions.

Fails (exit 1) when any known placeholder or review-only artifact is present in
the public thesis sources.

Usage:
    python scripts/check_tex_placeholders.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PLACEHOLDERS = [
    "[To be filled]",
    "[Insert Data]",
    "[Pending]",
    "[TBD]",
    "[YES/NO]",
    "[Observation",
    "待填入",
    "由模擬管線自動填入",
    "Section ??",
    "Table ??",
    "run pipeline",
    "elementsofai.com/zh",
    "conservative judges display r...",
]
ALL_CAPS_PLACEHOLDER = re.compile(r"\[[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\]")
BROKEN_PI_PLACEHOLDER = re.compile(r"\\Pi\(\s*\)")
PROJECT_ROOT = Path(__file__).resolve().parents[1]


SKIP_DIRS = {".git", "node_modules", ".worktrees", ".venv", ".venv_erh", ".venv_new", ".venv_sphinx"}
THESIS_FILES = {
    PROJECT_ROOT / "latex" / "ethical_riemann_hypothesis.tex",
    PROJECT_ROOT / "latex" / "ethical_riemann_hypothesis_en.tex",
    PROJECT_ROOT / "latex" / "ethical_riemann_hypothesis_zh.tex",
}


def main() -> int:
    found = []
    for path in sorted(THESIS_FILES):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            for ph in PLACEHOLDERS:
                if ph in text:
                    found.append((path, ph))
            for match in ALL_CAPS_PLACEHOLDER.finditer(text):
                found.append((path, match.group(0)))
            for match in BROKEN_PI_PLACEHOLDER.finditer(text):
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
