"""
Service layer for interfacing with erh_core modules.

This module provides a bridge between the FastAPI backend and the erh_core
Python library for ethical rule verification and analysis.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add project root to path to import erh_core
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from erh_core.core.axioms import verify_all_axioms
    from erh_core.analysis.erh_checks import check_erh_bound
    from erh_core.analysis.edge_cases import analyze_edge_cases
except ImportError as e:
    logger.warning(f"Could not import erh_core modules: {e}. Verification may be limited.")
    verify_all_axioms = None
    check_erh_bound = None
    analyze_edge_cases = None


def verify_latex_rule(latex_content: str) -> Dict[str, Any]:
    """
    Verify a LaTeX ethical rule against erh_core constraints.

    Args:
        latex_content: The LaTeX string to verify

    Returns:
        Dictionary containing verification results including:
        - risk_score: Float between 0.0 and 1.0
        - violations: List of violation objects
        - is_valid: Boolean indicating if rule passes
        - warnings: List of warning messages
    """
    violations: List[Dict[str, Any]] = []
    warnings: List[str] = []
    risk_score = 0.0

    try:
        # Basic validation - check if LaTeX content is non-empty
        if not latex_content or not latex_content.strip():
            violations.append({
                "type": "empty_rule",
                "severity": "high",
                "message": "LaTeX rule content cannot be empty",
                "line": None,
                "column": None,
            })
            risk_score = 1.0
            return {
                "risk_score": risk_score,
                "violations": violations,
                "is_valid": False,
                "warnings": warnings,
            }

        # Check for common security/ethical constraint violations
        # This is a simplified check - in production, you'd parse LaTeX and check structure
        if "\\bypass" in latex_content.lower() or "\\override" in latex_content.lower():
            violations.append({
                "type": "security_bypass",
                "severity": "critical",
                "message": "Rule contains potential security bypass commands",
                "line": None,
                "column": None,
            })
            risk_score = max(risk_score, 0.9)

        # Check for unbalanced brackets (simplified)
        open_braces = latex_content.count("{")
        close_braces = latex_content.count("}")
        if open_braces != close_braces:
            warnings.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")

        # TODO: Integrate with erh_core.analysis modules for deeper verification
        # For now, return basic validation
        if risk_score == 0.0 and len(violations) == 0:
            risk_score = 0.1  # Low risk for basic valid rules

        return {
            "risk_score": risk_score,
            "violations": violations,
            "is_valid": len([v for v in violations if v.get("severity") in ("high", "critical")]) == 0,
            "warnings": warnings,
        }

    except Exception as e:
        logger.error(f"Error verifying LaTeX rule: {e}", exc_info=True)
        violations.append({
            "type": "verification_error",
            "severity": "high",
            "message": f"Error during verification: {str(e)}",
            "line": None,
            "column": None,
        })
        return {
            "risk_score": 0.8,
            "violations": violations,
            "is_valid": False,
            "warnings": warnings,
        }


def analyze_rule_security(latex_content: str) -> Dict[str, Any]:
    """
    Perform security analysis on a LaTeX rule.

    Args:
        latex_content: The LaTeX string to analyze

    Returns:
        Dictionary containing security analysis results
    """
    result = verify_latex_rule(latex_content)

    # Add additional security metrics
    security_metrics = {
        "complexity_score": len(latex_content) / 1000.0,  # Simplified complexity
        "has_conditions": "\\if" in latex_content or "\\when" in latex_content,
        "has_loops": "\\foreach" in latex_content or "\\loop" in latex_content,
    }

    result["security_metrics"] = security_metrics
    return result

