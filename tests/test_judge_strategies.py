"""
Unit tests for judgment strategies and ERH determination algorithms.

Tests cover:
- Different judge types (Biased, Noisy, Conservative, Radical)
- ERH bound checking
- Error growth analysis
- Ethical prime selection strategies
"""

import pytest
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'simulation')))

from simulation.core.action_space import Action, generate_world
from simulation.core.judgement_system import (
    BiasedJudge, NoisyJudge, ConservativeJudge, RadicalJudge, batch_evaluate
)
# simulation.core re-exports from erh_core.core; no simulation.core.ethical_primes submodule
from erh_core.core.ethical_primes import (
    select_ethical_primes, compute_Pi_and_error, analyze_error_growth
)
from simulation.analysis.erh_checks import check_erh_bound


class TestJudgeStrategies:
    """Test different judgment strategies."""
    
    def test_biased_judge(self):
        """Test BiasedJudge produces systematic bias."""
        judge = BiasedJudge(bias_strength=0.2)
        actions = generate_world(num_actions=100, random_seed=42)
        
        # Evaluate actions
        for action in actions[:10]:
            judgment = judge.judge(action)
            assert isinstance(judgment, (int, float))
            assert 0 <= judgment <= 1
        
        # Test that bias increases with complexity
        simple_action = Action(c=1, v=0.5, w=1.0)
        complex_action = Action(c=50, v=0.5, w=1.0)
        
        simple_judgment = judge.judge(simple_action)
        complex_judgment = judge.judge(complex_action)
        
        # Complex actions should have more bias
        assert abs(complex_judgment - 0.5) >= abs(simple_judgment - 0.5)
    
    def test_noisy_judge(self):
        """Test NoisyJudge adds random noise."""
        judge = NoisyJudge(noise_scale=0.3, random_seed=42)
        action = Action(c=10, v=0.5, w=1.0)
        
        judgments = [judge.judge(action) for _ in range(10)]
        
        # Should have variation due to noise
        assert np.std(judgments) > 0.01
    
    def test_conservative_judge(self):
        """Test ConservativeJudge tends to avoid extremes."""
        judge = ConservativeJudge(threshold=0.5)
        extreme_action = Action(c=10, v=0.9, w=1.0)  # High value
        
        judgment = judge.judge(extreme_action)
        
        # Conservative judge should pull toward threshold
        assert judgment < extreme_action.v
    
    def test_radical_judge(self):
        """Test RadicalJudge amplifies differences."""
        judge = RadicalJudge(amplification=1.5)
        moderate_action = Action(c=10, v=0.6, w=1.0)
        
        judgment = judge.judge(moderate_action)
        
        # Radical judge should amplify away from 0.5
        assert abs(judgment - 0.5) > abs(moderate_action.v - 0.5)


class TestERHDetermination:
    """Test ERH bound checking and error growth analysis."""
    
    def test_erh_bound_check(self):
        """Test ERH-style bound checking."""
        # Create synthetic error data that satisfies ERH
        x_values = np.arange(1, 101)
        E_x = 0.5 * np.sqrt(x_values)  # |E(x)| = 0.5 * sqrt(x), satisfies ERH
        
        result = check_erh_bound(E_x, x_values, C=1.0, epsilon=0.1)
        
        assert result['erh_satisfied'] is True
        assert result['max_ratio'] < 1.5  # Should be within slack
        assert result['violation_rate'] < 0.05  # Few violations allowed
    
    def test_erh_bound_violation(self):
        """Test ERH bound violation detection."""
        # Create error data that violates ERH
        x_values = np.arange(1, 101)
        E_x = 2.0 * (x_values ** 0.8)  # Grows faster than sqrt(x)
        
        result = check_erh_bound(E_x, x_values, C=1.0, epsilon=0.1)
        
        # Should detect violation
        assert result['erh_satisfied'] is False or result['violation_rate'] > 0.1
    
    def test_error_growth_analysis(self):
        """Test error growth exponent estimation."""
        # Create synthetic error with known exponent
        x_values = np.arange(1, 101)
        true_alpha = 0.4
        E_x = 1.0 * (x_values ** true_alpha)
        
        analysis = analyze_error_growth(E_x, x_values)
        
        assert 'estimated_exponent' in analysis
        assert not np.isnan(analysis['estimated_exponent'])
        # Should be close to true exponent
        assert abs(analysis['estimated_exponent'] - true_alpha) < 0.1
        assert 'alpha_ci_low' in analysis
        assert 'alpha_ci_high' in analysis
    
    def test_ethical_prime_selection(self):
        """Test ethical prime selection strategies."""
        actions = generate_world(num_actions=200, random_seed=42)
        judge = BiasedJudge(bias_strength=0.2)
        
        # Evaluate and mark mistakes
        for action in actions:
            judgment = judge.judge(action)
            action.delta = judgment - action.v
            action.mistake_flag = 1 if abs(action.delta) > 0.3 else 0
        
        # Test importance strategy
        primes_importance = select_ethical_primes(
            actions, strategy='importance', importance_quantile=0.9
        )
        assert len(primes_importance) > 0
        assert all(p.mistake_flag == 1 for p in primes_importance)
        
        # Test complexity strategy
        primes_complexity = select_ethical_primes(
            actions, strategy='complexity', importance_quantile=0.9
        )
        assert len(primes_complexity) > 0
        
        # Test hybrid strategy
        primes_hybrid = select_ethical_primes(
            actions, strategy='hybrid', importance_quantile=0.9
        )
        assert len(primes_hybrid) > 0


class TestPiBErrorComputation:
    """Test Π(x), B(x), and E(x) computation."""
    
    def test_compute_pi_b_e(self):
        """Test computation of Pi, B, and E functions."""
        actions = generate_world(num_actions=200, random_seed=42)
        judge = BiasedJudge(bias_strength=0.2)
        
        # Evaluate actions
        for action in actions:
            judgment = judge.judge(action)
            action.delta = judgment - action.v
            action.mistake_flag = 1 if abs(action.delta) > 0.3 else 0
        
        primes = select_ethical_primes(actions, importance_quantile=0.9)
        
        Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=50)
        
        assert len(Pi_x) == 50
        assert len(B_x) == 50
        assert len(E_x) == 50
        assert len(x_vals) == 50
        
        # E(x) should equal Pi(x) - B(x)
        np.testing.assert_allclose(E_x, Pi_x - B_x, rtol=1e-10)
        
        # Pi(x) should be non-decreasing
        assert np.all(np.diff(Pi_x) >= 0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

