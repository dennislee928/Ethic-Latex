"""
Cloud IAM Logic Audit / Zero-Trust CSPM adapter (Phase 2).

Treats each IAM grant as a decision and measures how far granted scope diverges
from a least-privilege baseline. ERH then tells us whether over-permission
*grows structurally* with policy complexity (logical privilege escalation) or
stays bounded (healthy, zero-trust-consistent).

Per grant:
    complexity (x) = breadth = actions x resources x principals
    value (V)      = least-privilege baseline (minimal scope actually needed)
    judgment (J)   = actual granted scope
    delta = J - V  => over-permission gap
    weight (w)     = asset criticality / internet exposure

Live integration: AWS IAM via boto3 (``pull_aws_grants``) when credentials are
available; otherwise grants are supplied inline.

Findings carry MITRE ATT&CK IOB-style metadata so they can feed a SIEM /
threat-intel dispatch center.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..contracts.schemas import EvaluateParams, EvaluateRequest, EvaluateResponse, Sample
from ..engine import evaluate as run_evaluate

router = APIRouter(prefix="/v1/iam", tags=["iam"])

# Mapping of over-permission to MITRE ATT&CK behavioral indicators (IOB).
_MITRE_IOB = {
    "wildcard_action": "T1098 (Account Manipulation)",
    "wildcard_resource": "T1530 (Data from Cloud Storage)",
    "admin_grant": "T1078.004 (Valid Accounts: Cloud Accounts)",
}


class IAMGrant(BaseModel):
    id: Optional[str] = None
    principal: str = Field(..., description="Who the grant is for.")
    actions: List[str] = Field(..., description="Granted actions (may include wildcards).")
    resources: List[str] = Field(..., description="Granted resources (may include wildcards).")
    needed_actions: List[str] = Field(
        default_factory=list, description="Least-privilege baseline actions actually required."
    )
    asset_criticality: int = Field(1, ge=1, le=10)
    internet_exposed: bool = False


class IAMAuditRequest(BaseModel):
    grants: List[IAMGrant]
    params: EvaluateParams = Field(default_factory=EvaluateParams)


def _baseline_scope(grant: IAMGrant) -> float:
    """Least-privilege baseline V: always the safe pole (+1).

    V is the ideal — a grant scoped exactly to what is needed. The actual grant
    J is measured against it, so the over-permission gap is ``J - V``.
    """
    return 1.0


def _granted_scope(grant: IAMGrant) -> float:
    """Actual granted scope J in [-1, 1]; -1 = maximally over-broad / over-granted.

    Penalizes wildcards, raw breadth, and low precision against the
    least-privilege baseline (granted actions not actually needed).
    """
    wild = any(a.strip() == "*" or a.strip().endswith(":*") for a in grant.actions)
    wild_res = any(r.strip() == "*" for r in grant.resources)
    breadth = len(grant.actions) + len(grant.resources)
    score = 1.0
    if wild:
        score -= 1.2
    if wild_res:
        score -= 0.8
    score -= min(0.8, breadth / 50.0)

    # Precision penalty: fraction of granted actions that are NOT needed.
    if grant.needed_actions:
        granted = set(grant.actions)
        if granted:
            precision = len(set(grant.needed_actions) & granted) / len(granted)
            score -= (1.0 - precision)  # 0 when perfectly scoped, up to -1 when none needed

    return float(max(-1.0, score))


def _iob_tags(grant: IAMGrant) -> List[str]:
    tags: List[str] = []
    if any(a.strip() == "*" or a.strip().endswith(":*") for a in grant.actions):
        tags.append(_MITRE_IOB["wildcard_action"])
    if any(r.strip() == "*" for r in grant.resources):
        tags.append(_MITRE_IOB["wildcard_resource"])
    if any("admin" in a.lower() or a.strip() == "*" for a in grant.actions):
        tags.append(_MITRE_IOB["admin_grant"])
    return sorted(set(tags))


def _effective_count(items: List[str]) -> int:
    """Count scope items; a wildcard expands to a large effective breadth."""
    wild = any(s.strip() == "*" or s.strip().endswith(":*") for s in items)
    base = len(items)
    return base + (40 if wild else 0)


def grants_to_samples(grants: List[IAMGrant]) -> List[Sample]:
    samples: List[Sample] = []
    for i, g in enumerate(grants):
        # Wildcards dominate breadth: a "*" grant is maximally broad, not size-1.
        breadth = max(1, _effective_count(g.actions) * _effective_count(g.resources))
        complexity = float(min(100.0, breadth))
        weight = float(g.asset_criticality * (2.0 if g.internet_exposed else 1.0))
        samples.append(
            Sample(
                id=g.id or f"iam-{i}",
                complexity=complexity,
                value=_baseline_scope(g),
                judgment=_granted_scope(g),
                weight=weight,
                context={"principal": g.principal, "mitre_iob": _iob_tags(g)},
            )
        )
    return samples


def pull_aws_grants(scope: str = "*") -> List[IAMGrant]:  # pragma: no cover - needs creds
    """Live AWS IAM pull via boto3. Requires configured AWS credentials."""
    import boto3  # optional dependency

    iam = boto3.client("iam")
    grants: List[IAMGrant] = []
    for user in iam.list_users().get("Users", []):
        name = user["UserName"]
        attached = iam.list_attached_user_policies(UserName=name).get("AttachedPolicies", [])
        actions: List[str] = []
        for pol in attached:
            ver = iam.get_policy(PolicyArn=pol["PolicyArn"])["Policy"]["DefaultVersionId"]
            doc = iam.get_policy_version(PolicyArn=pol["PolicyArn"], VersionId=ver)
            statements = doc["PolicyVersion"]["Document"].get("Statement", [])
            for st in statements if isinstance(statements, list) else [statements]:
                act = st.get("Action", [])
                actions.extend(act if isinstance(act, list) else [act])
        grants.append(IAMGrant(id=name, principal=name, actions=actions or ["*"], resources=["*"]))
    return grants


@router.post("/audit", response_model=EvaluateResponse)
def audit_iam(req: IAMAuditRequest) -> EvaluateResponse:
    samples = grants_to_samples(req.grants)
    return run_evaluate(
        EvaluateRequest(samples=samples, params=req.params, judge_name="iam-cspm")
    )
