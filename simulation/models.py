"""
Pydantic models for runtime validation of simulation data.

Replaces custom dataclasses with type-safe, validated models for Action
and Judgment per Phase 1 of the ERH enhancement plan.
"""

from __future__ import annotations

from typing import Optional, List, Tuple

from pydantic import BaseModel, Field


# Canonical ethical principles ontology (Deontology, Utilitarianism, etc.)
# Used for principled conflict counting in calculate_complexity.
ETHICAL_PRINCIPLES: List[str] = [
    "Deontology",           # Rule/duty-based
    "Utilitarianism",       # Consequence-based
    "Virtue_Ethics",       # Character-based
    "Care_Ethics",         # Relationship-based
    "Rights_Theory",       # Entitlement-based
]


class Action(BaseModel):
    """
    Represents a single action/case in the moral judgment space.

    Attributes
    ----------
    id : int
        Unique identifier for the action
    c : int
        Complexity level (positive integer)
    V : float
        True moral value (ground truth), typically in [-1, 1]
        -1 = extremely immoral, 0 = neutral, +1 = extremely moral
    w : float
        Importance weight (e.g., number of people affected, severity)
    J : Optional[float]
        Judgment value assigned by a judge (initially None)
    delta : Optional[float]
        Error: Δ(a) = J(a) - V(a) (initially None)
    mistake_flag : Optional[int]
        Binary indicator: 1 if |Δ| > τ, 0 otherwise (initially None)
    severity : Optional[float]
        Fuzzy severity (0-1) for continuous error assessment
    """

    model_config = {"validate_assignment": True}

    id: int
    c: int = Field(..., description="Complexity level (positive integer)")
    V: float = Field(..., ge=-1.0, le=1.0, description="True moral value (ground truth)")
    w: float = Field(..., ge=1e-10, description="Importance weight")
    J: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Judgment value")
    delta: Optional[float] = Field(None, description="Error: J - V")
    mistake_flag: Optional[int] = Field(None, ge=0, le=1, description="Misjudgment indicator")
    severity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Fuzzy severity")
    conflicting_principles: Optional[int] = Field(
        None,
        ge=0,
        description="Number of conflicting ethical principles (e.g. Deontology vs Utilitarianism)",
    )
    description: Optional[str] = Field(
        None,
        description="Optional text description for token-length complexity proxy",
    )
    active_principles: Optional[List[int]] = Field(
        None,
        description="Indices into ETHICAL_PRINCIPLES; which principles apply to this action.",
    )
    principle_conflict_pairs: Optional[List[Tuple[int, int]]] = Field(
        None,
        description="List of (i,j) principle indices that conflict for this action.",
    )

    def __repr__(self) -> str:
        return f"Action(id={self.id}, c={self.c}, V={self.V:.2f}, w={self.w:.2f})"


class Judgment(BaseModel):
    """
    Runtime validation model for simulation judgment data.

    Used for validating judgment outputs and API serialization.
    """

    action_id: int
    J: float = Field(..., ge=-1.0, le=1.0)
    V: float = Field(..., ge=-1.0, le=1.0)
    delta: float
    mistake_flag: int = Field(..., ge=0, le=1)
    c: Optional[int] = None
    w: Optional[float] = None
