"""Assemble the ERH Guardian Strands agent."""

from __future__ import annotations

import os
from typing import Optional

from strands import Agent
from strands.models import BedrockModel

from .gate import ApprovalCallback, GuardianGate
from .profiles import ValueProfile
from .tools import ALL_TOOLS

SYSTEM_PROMPT = """\
You are ERH Guardian, a values-aligned professional assistant for IT and
security work. Your defining behavior is *score before act*:

1. Before recommending or executing anything consequential, evaluate it with
   your ERH tools (score_text, erh_evaluate_actions, audit_iam_grants).
2. Always surface the numbers behind a verdict: risk_score (0-100),
   erh_satisfied, and the error-growth exponent (healthy is about 0.5;
   drifting toward 1 means systematic misjudgment).
3. Consequential actions (apply_iam_remediation) pass through the
   GuardianGate. If the gate blocks an action, do not retry it verbatim:
   explain the risk in plain language and propose a safer alternative.
4. Respect the user's value profile: their risk threshold and protected
   topics are hard boundaries, not suggestions.
5. Be transparent about uncertainty. Never claim an action is safe without a
   score, and never hide a failed ERH bound check.
"""


def build_guardian(
    profile: Optional[ValueProfile] = None,
    approval_callback: Optional[ApprovalCallback] = None,
    model_id: Optional[str] = None,
    extra_tools: Optional[list] = None,
) -> tuple[Agent, GuardianGate]:
    """Build the guardian agent and its gate (exposed for audit access).

    ``extra_tools`` lets callers add MCP-discovered tools (see mcp_link):
    pass ``mcp_client.list_tools_sync()`` while the client context is open.
    """
    profile = profile or ValueProfile.load()
    gate = GuardianGate(profile, approval_callback=approval_callback)
    model = BedrockModel(
        model_id=model_id or os.environ.get("ERH_GUARDIAN_MODEL", "global.anthropic.claude-sonnet-4-6"),
        region_name=os.environ.get("AWS_REGION", "us-west-2"),
        temperature=0.3,
    )
    agent = Agent(
        model=model,
        tools=ALL_TOOLS + list(extra_tools or []),
        system_prompt=SYSTEM_PROMPT,
        hooks=[gate],
        name="erh-guardian",
        description="Values-aligned assistant; every consequential action is ERH-scored and human-gated.",
    )
    return agent, gate
