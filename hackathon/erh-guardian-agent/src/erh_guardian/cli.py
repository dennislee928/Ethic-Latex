"""ERH Guardian CLI: interactive chat (Bedrock) and an offline demo scenario."""

from __future__ import annotations

import argparse
import json
import sys

from .gate import GateDecision, decide
from .profiles import ValueProfile
from .tools import audit_iam_grants, score_text

DEMO_GRANTS = [
    {
        "principal": "ci-deployer",
        "actions": ["s3:PutObject", "s3:GetObject"],
        "resources": ["arn:aws:s3:::deploy-bucket/*"],
        "needed_actions": ["s3:PutObject", "s3:GetObject"],
        "asset_criticality": 3,
    },
    {
        "principal": "intern-admin",
        "actions": ["*"],
        "resources": ["*"],
        "needed_actions": ["s3:GetObject"],
        "asset_criticality": 9,
        "internet_exposed": True,
    },
    {
        "principal": "analytics-reader",
        "actions": ["athena:*", "glue:*", "s3:*"],
        "resources": ["*"],
        "needed_actions": ["athena:StartQueryExecution", "s3:GetObject"],
        "asset_criticality": 6,
    },
]


def _terminal_approval(tool_name: str, action_text: str, decision: GateDecision) -> bool:
    print(f"\n=== GuardianGate: human approval required ===")
    print(f"  tool:   {tool_name}")
    print(f"  action: {action_text}")
    print(f"  why:    {decision.reason()}")
    answer = input("Approve this action? [y/N] ").strip().lower()
    return answer in ("y", "yes")


def cmd_demo() -> int:
    """Offline demo: ERH-audit fixture IAM grants, then gate a risky remediation."""
    profile = ValueProfile.load()
    print(f"Value profile: threshold {profile.risk_threshold}/100, "
          f"protected topics: {profile.protected_topics}")

    print("\n[1] ERH audit of IAM grants (fixtures, no AWS calls):")
    verdict = audit_iam_grants(grants=DEMO_GRANTS)
    print(json.dumps(verdict, indent=2))

    print("\n[2] GuardianGate decisions on two proposed remediations:")
    safe = decide(profile, "apply_iam_remediation", {
        "principal": "analytics-reader",
        "remediation": "Scope athena and s3 actions to the two operations actually used.",
    })
    risky = decide(profile, "apply_iam_remediation", {
        "principal": "intern-admin",
        "remediation": "Keep wildcard admin access and attack surface, bypass review, "
                       "override safety checks to unblock the intern.",
    })
    for d in (safe, risky):
        status = "NEEDS HUMAN APPROVAL" if d.needs_approval else "auto-approved"
        print(f"  - {d.tool_name} for risk {d.risk_score:.0f}/100 -> {status}"
              + (f" ({d.reason()})" if d.needs_approval else ""))

    print("\n[3] Text scoring:")
    print(json.dumps(score_text(text="Rotate the leaked key and notify the owner."), indent=2))
    return 0


def cmd_chat() -> int:
    """Interactive guardian backed by Bedrock (requires AWS credentials)."""
    from .guardian import build_guardian

    agent, gate = build_guardian(approval_callback=_terminal_approval)
    print("ERH Guardian ready (Ctrl-D to exit).")
    try:
        while True:
            try:
                prompt = input("\nyou> ").strip()
            except EOFError:
                break
            if not prompt:
                continue
            agent(prompt)
            print()
    except KeyboardInterrupt:
        pass
    if gate.audit_log:
        print(f"\n[audit] {len(gate.audit_log)} gate decisions this session, "
              f"{sum(1 for d in gate.audit_log if d.needs_approval)} required approval.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="erh-guardian")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="offline demo scenario (no AWS calls)")
    sub.add_parser("chat", help="interactive agent on Bedrock")
    args = parser.parse_args(argv)
    return cmd_demo() if args.command == "demo" else cmd_chat()


if __name__ == "__main__":
    sys.exit(main())
