"""
Axiomatic Framework Module

This module defines formal axioms for judgment systems and verifies
logical consistency properties.
"""

from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from .action_space import Action


class JudgmentAxiom(ABC):
    """
    Abstract base class for judgment system axioms.
    """
    
    @abstractmethod
    def check(self, actions: List[Action], judge) -> tuple[bool, str]:
        """
        Check if the axiom is satisfied.
        
        Returns
        -------
        (satisfied, explanation) : tuple
            Whether axiom is satisfied and explanation
        """
        pass


class BoundednessAxiom(JudgmentAxiom):
    """
    Axiom: Judgments should be bounded (e.g., in [-1, 1]).
    """
    
    def check(self, actions: List[Action], judge) -> tuple[bool, str]:
        """Check that all judgments are bounded."""
        violations = []
        for action in actions:
            J = judge.judge(action)
            if abs(J) > 1.0:
                violations.append(action.id)
        
        if len(violations) == 0:
            return True, "All judgments are bounded in [-1, 1]"
        else:
            return False, f"Found {len(violations)} violations: judgments outside [-1, 1]"


class ConsistencyAxiom(JudgmentAxiom):
    """
    Axiom: Same action should receive same judgment (deterministic).
    """
    
    def check(self, actions: List[Action], judge) -> tuple[bool, str]:
        """Check consistency (determinism)."""
        # Test: judge same action multiple times
        if len(actions) == 0:
            return True, "No actions to test"
        
        test_action = actions[0]
        judgments = [judge.judge(test_action) for _ in range(10)]
        
        # Check if all judgments are the same (within numerical precision)
        if all(abs(j - judgments[0]) < 1e-10 for j in judgments):
            return True, "Judge is deterministic (consistent)"
        else:
            std = __import__('numpy').std(judgments)
            return False, f"Judge is non-deterministic: std={std:.6f}"


class MonotonicityAxiom(JudgmentAxiom):
    """
    Axiom: If V(a1) > V(a2) and both have same complexity, then J(a1) ≥ J(a2).
    """
    
    def check(self, actions: List[Action], judge) -> tuple[bool, str]:
        """Check monotonicity property."""
        # Group by complexity
        by_complexity = {}
        for action in actions:
            c = action.c
            if c not in by_complexity:
                by_complexity[c] = []
            by_complexity[c].append(action)
        
        violations = 0
        total_pairs = 0
        
        for c, group in by_complexity.items():
            if len(group) < 2:
                continue
            
            # Check all pairs
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    a1, a2 = group[i], group[j]
                    if a1.V > a2.V:
                        J1 = judge.judge(a1)
                        J2 = judge.judge(a2)
                        if J1 < J2:
                            violations += 1
                        total_pairs += 1
        
        if total_pairs == 0:
            return True, "Insufficient data to test monotonicity"
        
        violation_rate = violations / total_pairs
        if violation_rate < 0.1:  # Allow 10% violations (for noisy judges)
            return True, f"Monotonicity mostly satisfied ({violation_rate:.1%} violations)"
        else:
            return False, f"Monotonicity violated: {violation_rate:.1%} of pairs"


class ErrorBoundednessAxiom(JudgmentAxiom):
    """
    Axiom: Error |Δ(a)| should be bounded for all actions.
    """
    
    def __init__(self, max_error: float = 2.0):
        self.max_error = max_error
    
    def check(self, actions: List[Action], judge) -> tuple[bool, str]:
        """Check that errors are bounded."""
        max_observed_error = 0.0
        violations = []
        
        for action in actions:
            J = judge.judge(action)
            error = abs(J - action.V)
            if error > self.max_error:
                violations.append(action.id)
            max_observed_error = max(max_observed_error, error)
        
        if len(violations) == 0:
            return True, f"All errors bounded: max = {max_observed_error:.3f}"
        else:
            return False, f"Found {len(violations)} violations: max error = {max_observed_error:.3f}"


def verify_all_axioms(actions: List[Action], judge) -> Dict:
    """
    Verify all axioms for a judgment system.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to test
    judge
        Judge instance
        
    Returns
    -------
    dict
        Verification results for each axiom
    """
    axioms = [
        BoundednessAxiom(),
        ConsistencyAxiom(),
        MonotonicityAxiom(),
        ErrorBoundednessAxiom()
    ]
    
    results = {}
    for axiom in axioms:
        axiom_name = axiom.__class__.__name__
        satisfied, explanation = axiom.check(actions, judge)
        results[axiom_name] = {
            'satisfied': satisfied,
            'explanation': explanation
        }
    
    # Overall consistency
    all_satisfied = all(r['satisfied'] for r in results.values())
    
    return {
        'all_satisfied': all_satisfied,
        'axioms': results,
        'summary': f"{sum(1 for r in results.values() if r['satisfied'])}/{len(axioms)} axioms satisfied"
    }

