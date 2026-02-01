"""
Code complexity metrics using Cyclomatic Complexity and Halstead Complexity.

Implements calculate_code_complexity(code_snippet) for use in the Security PoC
when analyzing LaTeX rules or code snippets. Provides concrete x values instead
of abstract complexity.
"""

from __future__ import annotations

import ast
import re
from typing import Literal


def _cyclomatic_complexity_python(code: str) -> int:
    """Compute cyclomatic complexity for Python code via AST."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 1

    complexity = 1
    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.If,
                ast.While,
                ast.For,
                ast.ExceptHandler,
                ast.With,
                ast.Assert,
                ast.comprehension,
                ast.BoolOp,
            ),
        ):
            complexity += 1
        elif isinstance(node, ast.If):
            complexity += len(node.orelse) if node.orelse else 1
    return max(1, complexity)


def _cyclomatic_complexity_latex(code: str) -> int:
    """Structural complexity for LaTeX: count control flow constructs."""
    patterns = [
        r"\\if\b",
        r"\\else\b",
        r"\\fi\b",
        r"\\loop\b",
        r"\\repeat\b",
        r"\\unless\b",
        r"\\unless\s",
        r"\\or\b",
        r"\\whiledo\s*\{",
        r"\\ifthenelse\s*\{",
    ]
    count = 1
    for p in patterns:
        count += len(re.findall(p, code, re.IGNORECASE))
    return max(1, count)


def _halstead_complexity(code: str) -> float:
    """Approximate Halstead complexity: vocabulary and length."""
    operators = set(re.findall(r"[=+\-*/%&|^<>!]=?|\.\.\.|and|or|not|\bif\b|\belse\b|\bfor\b|\bwhile\b", code))
    operands = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", code)) - operators
    n1, n2 = len(operators), len(operands)
    N1 = sum(len(re.findall(re.escape(op), code)) for op in operators)
    N2 = sum(len(re.findall(r"\b" + re.escape(op) + r"\b", code)) for op in operands)
    N = N1 + N2
    n = n1 + n2
    if n == 0:
        return 1.0
    volume = N * (n ** 0.5) if n > 0 else 1.0
    return max(1.0, volume / 100.0)


def calculate_code_complexity(
    code_snippet: str,
    method: Literal["cyclomatic", "halstead", "auto"] = "auto",
) -> float:
    """
    Compute concrete complexity score for a code snippet.

    Uses Cyclomatic Complexity for Python/structured code, or Halstead for
    general text. Returns value in [1, 100] for use as ERH complexity x.

    Parameters
    ----------
    code_snippet : str
        Source code or LaTeX content to analyze
    method : 'cyclomatic' | 'halstead' | 'auto'
        - cyclomatic: Decision points (if/else/loop etc.)
        - halstead: Vocabulary-based metric
        - auto: Use cyclomatic for Python/LaTeX, halstead as fallback

    Returns
    -------
    float
        Complexity score c in [1, 100]

    Examples
    --------
    >>> calculate_code_complexity("if x > 0: return 1")
    2.0
    >>> calculate_code_complexity("\\\\ifx\\\\abc\\\\fi")
    2.0
    """
    if not code_snippet or not code_snippet.strip():
        return 1.0

    code = code_snippet.strip()

    if method == "cyclomatic":
        if "def " in code or "class " in code or "import " in code or "lambda " in code:
            raw = float(_cyclomatic_complexity_python(code))
        elif "\\" in code:
            raw = float(_cyclomatic_complexity_latex(code))
        else:
            raw = float(_cyclomatic_complexity_python(code))
    elif method == "halstead":
        raw = _halstead_complexity(code)
    else:
        if "def " in code or "class " in code or "import " in code or "lambda " in code:
            raw = float(_cyclomatic_complexity_python(code))
        elif "\\if" in code or "\\else" in code or "\\fi" in code or "\\loop" in code:
            raw = float(_cyclomatic_complexity_latex(code))
        else:
            raw = _halstead_complexity(code)

    return float(min(100.0, max(1.0, raw)))
