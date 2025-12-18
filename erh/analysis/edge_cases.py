"""
Edge Case Analysis Module

This module tests the ERH framework in extreme cases to ensure
logical completeness and consistency.
"""

import numpy as np
from typing import List, Dict, Optional
from .action_space import Action
from ..core.ethical_primes import compute_Pi_and_error, analyze_error_growth
from ..core.judgement_system import BaseJudge


class PerfectJudge(BaseJudge):
    """Perfect judge with no errors."""
    
    def judge(self, action: Action) -> float:
        return action.V


class RandomJudge(BaseJudge):
    """Completely random judge."""
    
    def judge(self, action: Action) -> float:
        return np.random.uniform(-1, 1)


class DeterministicBiasJudge(BaseJudge):
    """Judge with fixed deterministic bias."""
    
    def __init__(self, bias: float = 0.5):
        super().__init__("DeterministicBiasJudge")
        self.bias = bias
    
    def judge(self, action: Action) -> float:
        return action.V + self.bias


def test_perfect_judge(actions: List[Action], tau: float = 0.3) -> Dict:
    """
    Test ERH framework with a perfect judge (no errors).
    
    Parameters
    ----------
    actions : List[Action]
        Actions to test
    tau : float, default=0.3
        Error threshold
        
    Returns
    -------
    dict
        Test results
    """
    judge = PerfectJudge()
    
    # Evaluate
    for action in actions:
        J = judge.judge(action)
        action.J = J
        action.delta = J - action.V
        action.mistake_flag = 1 if abs(action.delta) > tau else 0
    
    mistakes = sum(1 for a in actions if a.mistake_flag == 1)
    
    # Try to compute Pi(x), B(x), E(x)
    from ..core.ethical_primes import select_ethical_primes
    primes = select_ethical_primes(actions)
    
    if len(primes) > 0:
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
        analysis = analyze_error_growth(E_x, x_vals)
    else:
        Pi_x = B_x = E_x = x_vals = np.array([])
        analysis = {'estimated_exponent': np.nan, 'erh_satisfied': True}
    
    return {
        'judge_type': 'Perfect',
        'mistakes': mistakes,
        'mistake_rate': mistakes / len(actions) if len(actions) > 0 else 0.0,
        'primes_found': len(primes),
        'pi_x_max': Pi_x[-1] if len(Pi_x) > 0 else 0,
        'e_x_max': E_x[-1] if len(E_x) > 0 else 0,
        'erh_satisfied': analysis.get('erh_satisfied', True),
        'exponent': analysis.get('estimated_exponent', np.nan),
        'interpretation': 'Perfect judge should have no mistakes and satisfy ERH trivially'
    }


def test_random_judge(actions: List[Action], tau: float = 0.3) -> Dict:
    """
    Test ERH framework with completely random judge.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to test
    tau : float, default=0.3
        Error threshold
        
    Returns
    -------
    dict
        Test results
    """
    judge = RandomJudge()
    
    # Evaluate
    for action in actions:
        J = judge.judge(action)
        action.J = J
        action.delta = J - action.V
        action.mistake_flag = 1 if abs(action.delta) > tau else 0
    
    mistakes = sum(1 for a in actions if a.mistake_flag == 1)
    
    from ..core.ethical_primes import select_ethical_primes
    primes = select_ethical_primes(actions)
    
    if len(primes) > 0:
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
        analysis = analyze_error_growth(E_x, x_vals)
    else:
        Pi_x = B_x = E_x = x_vals = np.array([])
        analysis = {'estimated_exponent': np.nan, 'erh_satisfied': False}
    
    return {
        'judge_type': 'Random',
        'mistakes': mistakes,
        'mistake_rate': mistakes / len(actions) if len(actions) > 0 else 0.0,
        'primes_found': len(primes),
        'pi_x_max': Pi_x[-1] if len(Pi_x) > 0 else 0,
        'e_x_max': E_x[-1] if len(E_x) > 0 else 0,
        'erh_satisfied': analysis.get('erh_satisfied', False),
        'exponent': analysis.get('estimated_exponent', np.nan),
        'interpretation': 'Random judge should have high error rate, likely violates ERH'
    }


def test_deterministic_bias(actions: List[Action], bias: float = 0.5, tau: float = 0.3) -> Dict:
    """
    Test ERH framework with deterministic bias.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to test
    bias : float, default=0.5
        Fixed bias value
    tau : float, default=0.3
        Error threshold
        
    Returns
    -------
    dict
        Test results
    """
    judge = DeterministicBiasJudge(bias=bias)
    
    # Evaluate
    for action in actions:
        J = judge.judge(action)
        action.J = J
        action.delta = J - action.V
        action.mistake_flag = 1 if abs(action.delta) > tau else 0
    
    mistakes = sum(1 for a in actions if a.mistake_flag == 1)
    
    from ..core.ethical_primes import select_ethical_primes
    primes = select_ethical_primes(actions)
    
    if len(primes) > 0:
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
        analysis = analyze_error_growth(E_x, x_vals)
    else:
        Pi_x = B_x = E_x = x_vals = np.array([])
        analysis = {'estimated_exponent': np.nan, 'erh_satisfied': False}
    
    return {
        'judge_type': f'DeterministicBias({bias})',
        'mistakes': mistakes,
        'mistake_rate': mistakes / len(actions) if len(actions) > 0 else 0.0,
        'primes_found': len(primes),
        'pi_x_max': Pi_x[-1] if len(Pi_x) > 0 else 0,
        'e_x_max': E_x[-1] if len(E_x) > 0 else 0,
        'erh_satisfied': analysis.get('erh_satisfied', False),
        'exponent': analysis.get('estimated_exponent', np.nan),
        'interpretation': f'Deterministic bias of {bias} should produce systematic errors'
    }


def test_edge_complexities(actions: List[Action], judge, tau: float = 0.3) -> Dict:
    """
    Test behavior at edge complexity values (x=1, x→∞).
    
    Parameters
    ----------
    actions : List[Action]
        Actions to test
    judge
        Judge instance
    tau : float, default=0.3
        Error threshold
        
    Returns
    -------
    dict
        Test results for edge cases
    """
    from ..core.judgement_system import evaluate_judgement
    from ..core.ethical_primes import select_ethical_primes
    
    # Evaluate
    evaluate_judgement(actions, judge, tau=tau)
    primes = select_ethical_primes(actions)
    
    # Test at x=1
    x1_primes = [p for p in primes if p.c == 1]
    
    # Test at high complexity
    max_complexity = max((a.c for a in actions), default=1)
    high_c_primes = [p for p in primes if p.c >= max_complexity * 0.9]
    
    # Compute Pi(x) for different X_max values
    results = {}
    for X_max in [10, 50, 100, 200]:
        if len(primes) > 0:
            Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=X_max)
            if len(E_x) > 0:
                analysis = analyze_error_growth(E_x, x_vals)
                results[X_max] = {
                    'Pi_max': Pi_x[-1] if len(Pi_x) > 0 else 0,
                    'E_max': E_x[-1] if len(E_x) > 0 else 0,
                    'exponent': analysis.get('estimated_exponent', np.nan),
                    'erh_satisfied': analysis.get('erh_satisfied', False)
                }
    
    return {
        'x1_primes': len(x1_primes),
        'high_complexity_primes': len(high_c_primes),
        'max_complexity': max_complexity,
        'results_by_X_max': results,
        'interpretation': 'Tests framework behavior at complexity boundaries'
    }


def run_all_edge_case_tests(actions: List[Action], tau: float = 0.3) -> Dict:
    """
    Run all edge case tests and return comprehensive results.
    
    Parameters
    ----------
    actions : List[Action]
        Actions to test
    tau : float, default=0.3
        Error threshold
        
    Returns
    -------
    dict
        All test results
    """
    results = {}
    
    # Test perfect judge
    results['perfect'] = test_perfect_judge(actions, tau)
    
    # Test random judge
    results['random'] = test_random_judge(actions, tau)
    
    # Test deterministic bias
    results['deterministic_bias'] = test_deterministic_bias(actions, bias=0.5, tau=tau)
    
    # Test edge complexities
    from ..core.judgement_system import BiasedJudge
    judge = BiasedJudge(bias_strength=0.2)
    results['edge_complexities'] = test_edge_complexities(actions, judge, tau)
    
    return results

