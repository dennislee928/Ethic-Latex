"""Value-alignment profiles: the user's boundaries the guardian enforces."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field


class ValueProfile(BaseModel):
    """A user's value-alignment profile.

    ``risk_threshold`` is on the ERH engine's 0-100 risk scale: any
    consequential action scoring above it requires explicit human approval.
    """

    name: str = "default"
    risk_threshold: float = Field(40.0, ge=0.0, le=100.0)
    protected_topics: List[str] = Field(
        default_factory=lambda: ["production credentials", "wildcard admin access"],
        description="Topics that always require human approval regardless of score.",
    )
    auto_approve_tools: List[str] = Field(
        default_factory=lambda: ["score_text", "erh_evaluate_actions", "audit_iam_grants"],
        description="Read-only tools that never need approval.",
    )

    @classmethod
    def load(cls, path: str | os.PathLike | None = None) -> "ValueProfile":
        path = path or os.environ.get("ERH_GUARDIAN_PROFILE")
        if path and Path(path).exists():
            return cls.model_validate(json.loads(Path(path).read_text()))
        return cls()

    def save(self, path: str | os.PathLike) -> None:
        Path(path).write_text(self.model_dump_json(indent=2))
