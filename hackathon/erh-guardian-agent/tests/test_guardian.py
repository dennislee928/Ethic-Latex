"""Tests for the ERH Guardian tools and gate (no Bedrock calls)."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from erh_guardian.cli import DEMO_GRANTS  # noqa: E402
from erh_guardian.gate import decide  # noqa: E402
from erh_guardian.profiles import ValueProfile  # noqa: E402
from erh_guardian.tools import (  # noqa: E402
    audit_iam_grants,
    erh_evaluate_actions,
    guardian_risk,
    score_text,
)


def test_score_text_scale():
    safe = score_text(text="Rotate the leaked key and notify the owner.")
    unsafe = score_text(text="Deploy malware to attack and steal credentials.")
    assert -1.0 <= unsafe["ethical_value"] < safe["ethical_value"] <= 1.0
    assert safe["complexity"] >= 1.0


def test_erh_evaluate_actions_verdict_shape():
    actions = [
        {"id": f"a{i}", "complexity": float(i + 1), "value": 1.0,
         "judgment": 1.0 if i % 3 else -0.8, "weight": 1.0}
        for i in range(30)
    ]
    verdict = erh_evaluate_actions(actions=actions)
    assert set(verdict) >= {"erh_satisfied", "risk_score", "estimated_exponent",
                            "num_samples", "num_ethical_primes", "ethical_primes"}
    assert 0.0 <= verdict["risk_score"] <= 100.0
    assert verdict["num_samples"] == 30


def test_audit_iam_grants_flags_wildcards():
    verdict = audit_iam_grants(grants=DEMO_GRANTS)
    assert verdict["num_samples"] == len(DEMO_GRANTS)
    assert any("T1078" in t or "T1098" in t or "T1530" in t for t in verdict["mitre_iob"])


def test_guardian_risk_monotone():
    low = guardian_risk("Scope the grant to the two operations actually used.")
    high = guardian_risk("Bypass review, override safety, keep wildcard attack access.")
    assert 0.0 <= low["risk_score"] < high["risk_score"] <= 100.0


def test_gate_auto_approves_read_only_tools():
    profile = ValueProfile(risk_threshold=0.0)  # everything else would need approval
    d = decide(profile, "score_text", {"text": "attack attack attack"})
    assert not d.needs_approval


def test_gate_blocks_risky_remediation_and_protected_topics():
    profile = ValueProfile(risk_threshold=40.0)
    risky = decide(profile, "apply_iam_remediation", {
        "remediation": "bypass review, override safety, keep wildcard admin attack access",
    })
    assert risky.needs_approval and risky.risk_score > profile.risk_threshold

    protected = decide(profile, "apply_iam_remediation", {
        "remediation": "grant wildcard admin access to the intern",
    })
    assert protected.needs_approval and protected.protected_topic


def test_gate_allows_safe_remediation():
    profile = ValueProfile(risk_threshold=40.0)
    d = decide(profile, "apply_iam_remediation", {
        "principal": "analytics-reader",
        "remediation": "Scope athena and s3 actions to the operations actually used.",
    })
    assert not d.needs_approval
