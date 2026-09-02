"""Strands @tool wrappers over the ERH engine's pure evaluate() contract."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from strands import tool

from ._bootstrap import ensure_erh_engine

ensure_erh_engine()

from erh_engine import EvaluateParams, EvaluateRequest, Sample, evaluate  # noqa: E402
from erh_engine.adapters.iam_cspm import (  # noqa: E402
    IAMAuditRequest,
    IAMGrant,
    audit_iam,
)
from erh_engine.adapters.scoring import ethical_value, text_complexity  # noqa: E402


def _verdict(resp) -> Dict[str, Any]:
    """Compact, agent-friendly projection of an EvaluateResponse."""
    return {
        "erh_satisfied": resp.erh_satisfied,
        "risk_score": resp.risk_score,
        "violation_rate": resp.violation_rate,
        "estimated_exponent": resp.estimated_exponent,
        "num_samples": resp.num_samples,
        "num_ethical_primes": resp.num_primes,
        "ethical_primes": [
            {"id": p.id, "complexity": p.complexity, "delta": p.delta}
            for p in (resp.primes or [])[:10]
        ],
    }


@tool
def score_text(text: str) -> Dict[str, float]:
    """Score a piece of text on the ERH ethical-value scale.

    Returns ethical_value in [-1, 1] (1 = safe, -1 = unsafe) and the
    heuristic decision complexity of the text.
    """
    return {
        "ethical_value": ethical_value(text),
        "complexity": text_complexity(text),
    }


@tool
def erh_evaluate_actions(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run a full Ethical Riemann Hypothesis evaluation over judged actions.

    Each action needs: id (str), complexity (float >= 0), value (float in
    [-1,1], the true/ideal judgment), judgment (float in [-1,1], the actual
    judgment), and optionally weight (float > 0) and context (dict).

    Returns the ERH verdict: erh_satisfied, risk_score (0-100), the fitted
    error-growth exponent (healthy ~= 0.5, systematic failure -> 1), and the
    top ethical primes (the critical misjudgments driving the risk).
    """
    samples = [Sample(**a) for a in actions]
    resp = evaluate(EvaluateRequest(samples=samples, judge_name="erh-guardian"))
    return _verdict(resp)


@tool
def audit_iam_grants(grants: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Audit IAM grants for least-privilege divergence, ERH-scored.

    Each grant needs: principal (str), actions (list[str]), resources
    (list[str]), and optionally needed_actions (list[str]), asset_criticality
    (1-10), internet_exposed (bool). Wildcards ('*') are treated as maximally
    broad and tagged with MITRE ATT&CK behavioral indicators.
    """
    req = IAMAuditRequest(grants=[IAMGrant(**g) for g in grants])
    resp = audit_iam(req)
    out = _verdict(resp)
    out["mitre_iob"] = sorted(
        {
            tag
            for g in req.grants
            for tag in _iam_tags(g)
        }
    )
    return out


def _iam_tags(grant: IAMGrant) -> List[str]:
    from erh_engine.adapters.iam_cspm import _iob_tags

    return _iob_tags(grant)


@tool
def audit_live_aws_iam(scope: str = "*") -> Dict[str, Any]:
    """Audit the *live* AWS account's IAM users via boto3 (requires credentials).

    Pulls attached user policies, converts them to grants, and returns the
    ERH least-privilege verdict for the whole account.
    """
    from erh_engine.adapters.iam_cspm import pull_aws_grants

    grants = pull_aws_grants(scope=scope)
    if not grants:
        return {"note": "No IAM users found in this account.", "num_samples": 0}
    resp = audit_iam(IAMAuditRequest(grants=grants))
    return _verdict(resp)


@tool
def apply_iam_remediation(principal: str, remediation: str, dry_run: bool = True) -> Dict[str, Any]:
    """Apply (or simulate) an IAM remediation for a principal.

    This is a consequential action: the GuardianGate scores the remediation
    text before this tool runs and requires human approval when the risk
    exceeds the user's value profile threshold. In this demo build only
    dry-run simulation is performed; no AWS mutation is issued.
    """
    return {
        "principal": principal,
        "remediation": remediation,
        "dry_run": True,
        "status": "simulated" if dry_run else "simulated (write disabled in demo build)",
    }


READ_ONLY_TOOLS = [score_text, erh_evaluate_actions, audit_iam_grants, audit_live_aws_iam]
CONSEQUENTIAL_TOOLS = [apply_iam_remediation]
ALL_TOOLS = READ_ONLY_TOOLS + CONSEQUENTIAL_TOOLS


def guardian_risk(text: str, context: Optional[str] = None) -> Dict[str, Any]:
    """Score a proposed action description on the 0-100 guardian risk scale.

    Used by the GuardianGate outside the agent loop. Maps the ethical value
    of the proposed action text (plus optional context) from [-1, 1] onto
    [0, 100] risk (value -1 -> risk 100, value +1 -> risk 0), weighted by the
    text's decision complexity.
    """
    blob = f"{text}\n{context}" if context else text
    v = ethical_value(blob)
    x = text_complexity(blob)
    base_risk = (1.0 - v) / 2.0 * 100.0
    # Higher-complexity decisions get a mild risk uplift (up to +20).
    uplift = min(20.0, x / 5.0)
    risk = float(min(100.0, base_risk + (uplift if base_risk > 0 else 0.0)))
    return {"risk_score": risk, "ethical_value": v, "complexity": x}
