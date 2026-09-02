"""GuardianGate: the human-in-the-loop hook that makes the agent trustworthy.

Before any consequential tool executes, the gate scores the proposed action
with the ERH scorer and against the user's value profile. If the risk exceeds
the profile threshold — or the action touches a protected topic — the tool
call is cancelled unless a human explicitly approves it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

from .profiles import ValueProfile
from .tools import guardian_risk

# approval_callback(tool_name, action_text, decision) -> True to approve
ApprovalCallback = Callable[[str, str, "GateDecision"], bool]


@dataclass
class GateDecision:
    tool_name: str
    action_text: str
    risk_score: float
    ethical_value: float
    threshold: float
    protected_topic: Optional[str]
    needs_approval: bool

    def reason(self) -> str:
        if self.protected_topic:
            return (
                f"touches protected topic '{self.protected_topic}' "
                f"(risk {self.risk_score:.0f}/100)"
            )
        return (
            f"risk {self.risk_score:.0f}/100 exceeds your threshold "
            f"{self.threshold:.0f}/100"
        )


def decide(profile: ValueProfile, tool_name: str, tool_input: Dict[str, Any]) -> GateDecision:
    """Pure gate decision: score the proposed action against the profile."""
    action_text = json.dumps(tool_input, ensure_ascii=False, default=str)
    scored = guardian_risk(action_text)
    lowered = action_text.lower()
    protected = next((t for t in profile.protected_topics if t.lower() in lowered), None)

    if tool_name in profile.auto_approve_tools:
        needs_approval = False
        protected = None
    else:
        needs_approval = protected is not None or scored["risk_score"] > profile.risk_threshold

    return GateDecision(
        tool_name=tool_name,
        action_text=action_text,
        risk_score=scored["risk_score"],
        ethical_value=scored["ethical_value"],
        threshold=profile.risk_threshold,
        protected_topic=protected,
        needs_approval=needs_approval,
    )


class GuardianGate(HookProvider):
    """Strands hook provider enforcing the value profile on every tool call."""

    def __init__(
        self,
        profile: ValueProfile,
        approval_callback: Optional[ApprovalCallback] = None,
    ) -> None:
        self.profile = profile
        self.approval_callback = approval_callback
        self.audit_log: list[GateDecision] = []

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeToolCallEvent, self._before_tool)

    def _before_tool(self, event: BeforeToolCallEvent) -> None:
        tool_name = event.tool_use.get("name", "")
        tool_input = event.tool_use.get("input", {}) or {}
        decision = decide(self.profile, tool_name, tool_input)
        self.audit_log.append(decision)

        if not decision.needs_approval:
            return

        approved = bool(self.approval_callback) and self.approval_callback(
            tool_name, decision.action_text, decision
        )
        if not approved:
            event.cancel_tool = (
                f"GuardianGate blocked '{tool_name}': {decision.reason()}. "
                "The human declined or was unavailable to approve this action. "
                "Explain the risk to the user and propose a safer alternative."
            )
