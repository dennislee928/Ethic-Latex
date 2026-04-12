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
from erh_core.analysis.erh_checks import check_erh_bound


class TestJudgeStrategies:
    """Test different judgment strategies."""
    
    def test_biased_judge(self):
        """Test BiasedJudge produces systematic bias."""
        judge = BiasedJudge(bias_strength=0.2)
        actions = generate_world(num_actions=100, random_seed=42)
        
        # Evaluate actions (judgment in [-1, 1] per Action model)
        for action in actions[:10]:
            judgment = judge.judge(action)
            assert isinstance(judgment, (int, float))
            assert -1 <= judgment <= 1
        
        # Test that bias increases with complexity
        simple_action = Action(id=0, c=1, V=0.5, w=1.0)
        complex_action = Action(id=1, c=50, V=0.5, w=1.0)
        
        simple_judgment = judge.judge(simple_action)
        complex_judgment = judge.judge(complex_action)
        
        # Complex actions should have more bias
        assert abs(complex_judgment - 0.5) >= abs(simple_judgment - 0.5)
    
    def test_noisy_judge(self):
        """Test NoisyJudge adds random noise."""
        np.random.seed(42)
        judge = NoisyJudge(noise_scale=0.3)
        action = Action(id=0, c=10, V=0.5, w=1.0)
        
        judgments = [judge.judge(action) for _ in range(10)]
        
        # Should have variation due to noise
        assert np.std(judgments) > 0.01
    
    def test_conservative_judge(self):
        """Test ConservativeJudge tends to avoid extremes."""
        judge = ConservativeJudge(threshold=0.5)
        extreme_action = Action(id=0, c=10, V=0.9, w=1.0)  # High value
        
        judgment = judge.judge(extreme_action)
        
        # Conservative judge should pull toward threshold
        assert judgment < extreme_action.V
    
    def test_radical_judge(self):
        """Test RadicalJudge amplifies differences."""
        judge = RadicalJudge(amplification=1.5)
        moderate_action = Action(id=0, c=10, V=0.6, w=1.0)
        
        judgment = judge.judge(moderate_action)
        
        # Radical judge should amplify away from 0.5
        assert abs(judgment - 0.5) > abs(moderate_action.V - 0.5)


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
            action.delta = judgment - action.V
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
            action.delta = judgment - action.V
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


# ---------------------------------------------------------------------------
# New test classes for Phase 1–4 additions
# ---------------------------------------------------------------------------

class TestERHCheckResult:
    """Tests for ERHCheckResult dataclass and its two companion functions."""

    def _make_erh_data(self):
        """Return a simple E_x, x_values pair that satisfies the ERH bound."""
        x = np.arange(1, 51, dtype=float)
        E = 0.5 * x ** 0.5  # exactly C·x^(0.5+0) — should satisfy
        return E, x

    def test_all_fields_populated(self):
        from erh_core.analysis.erh_checks import check_erh_bound_structured, ERHCheckResult
        E, x = self._make_erh_data()
        result = check_erh_bound_structured(E, x, C=1.0, epsilon=0.1,
                                            slack_factor=1.5,
                                            allowed_violation_rate=0.05,
                                            judge_name="TestJudge")
        assert isinstance(result, ERHCheckResult)
        assert result.C == 1.0
        assert result.epsilon == 0.1
        assert result.slack_factor == 1.5
        assert result.confidence_level == pytest.approx(0.95)
        assert result.sample_size == result.num_points
        assert result.judge_name == "TestJudge"
        assert isinstance(result.bound_type, str)
        assert isinstance(result.erh_satisfied, bool)
        assert np.isfinite(result.violation_rate)
        assert np.isfinite(result.max_ratio)

    def test_check_erh_bound_still_returns_dict(self):
        """Backward compatibility: original function must still return a plain dict."""
        from erh_core.analysis.erh_checks import check_erh_bound
        E, x = self._make_erh_data()
        result = check_erh_bound(E, x)
        assert isinstance(result, dict)
        assert "erh_satisfied" in result
        assert "max_ratio" in result
        assert "violation_rate" in result
        assert "num_points" in result

    def test_judge_and_check_erh_end_to_end(self):
        from erh_core.analysis.erh_checks import judge_and_check_erh, ERHCheckResult
        from erh_core.core.action_space import generate_world
        from erh_core.core.judgement_system import BiasedJudge, evaluate_judgement
        from erh_core.core.ethical_primes import select_ethical_primes, compute_Pi_and_error

        actions = generate_world(num_actions=200, random_seed=0)
        judge = BiasedJudge(bias_strength=0.1, noise_scale=0.05)
        evaluate_judgement(actions, judge, tau=0.3)

        primes = select_ethical_primes(actions)
        x_values, Pi_x, E_x = compute_Pi_and_error(actions, primes)

        result = judge_and_check_erh(actions, judge, E_x, x_values, log=False)
        assert isinstance(result, ERHCheckResult)
        assert result.judge_name == judge.name
        assert 0.0 <= result.violation_rate <= 1.0


class TestExplainability:
    """Tests for DecisionTrace, explain(), and trace storage."""

    def _action(self):
        return Action(id=1, c=50, V=0.4, w=1.0)

    def test_explain_returns_decision_trace(self):
        from erh_core.core.judgement_system import BiasedJudge, DecisionTrace
        judge = BiasedJudge()
        action = self._action()
        action.J = judge.judge(action)
        trace = judge.explain(action)
        assert isinstance(trace, DecisionTrace)
        assert trace.judge_name == judge.name
        assert trace.action_id == action.id

    def test_top_features_nonempty(self):
        from erh_core.core.judgement_system import NoisyJudge
        judge = NoisyJudge()
        action = self._action()
        action.J = judge.judge(action)
        trace = judge.explain(action)
        assert len(trace.top_features) > 0
        for name, val in trace.top_features:
            assert isinstance(name, str)
            assert isinstance(val, float)

    def test_trace_storage_off_by_default(self):
        from erh_core.core.judgement_system import ConservativeJudge
        judge = ConservativeJudge()
        action = self._action()
        judge.judge(action)
        assert len(judge.get_traces()) == 0

    def test_enable_and_retrieve_traces(self):
        from erh_core.core.judgement_system import RadicalJudge, evaluate_judgement
        from erh_core.core.action_space import generate_world
        judge = RadicalJudge()
        judge.enable_trace_storage()
        actions = generate_world(num_actions=10, random_seed=1)
        for a in actions:
            a.J = judge.judge(a)
            judge.explain(a)
        traces = judge.get_traces()
        assert len(traces) == 10
        judge.clear_traces()
        assert len(judge.get_traces()) == 0


class TestCalibration:
    """Tests for calibrate() and calibrated_confidence()."""

    def _calibration_actions(self, judge, n=80):
        from erh_core.core.action_space import generate_world
        from erh_core.core.judgement_system import evaluate_judgement
        actions = generate_world(num_actions=n, random_seed=7)
        evaluate_judgement(actions, judge, tau=0.3)
        return actions

    def test_platt_calibration_changes_confidence(self):
        from erh_core.core.judgement_system import BiasedJudge
        judge = BiasedJudge(bias_strength=0.4)
        actions = self._calibration_actions(judge)
        action = actions[0]
        conf_before = judge.calibrated_confidence(action)
        judge.calibrate(actions, method="platt")
        conf_after = judge.calibrated_confidence(action)
        # Both must be in [0, 1]; calibration may change the value
        assert 0.0 <= conf_before <= 1.0
        assert 0.0 <= conf_after <= 1.0

    def test_isotonic_calibration(self):
        from erh_core.core.judgement_system import NoisyJudge
        judge = NoisyJudge(noise_scale=0.4)
        actions = self._calibration_actions(judge, n=100)
        judge.calibrate(actions, method="isotonic")
        action = actions[5]
        conf = judge.calibrated_confidence(action)
        assert 0.0 <= conf <= 1.0

    def test_uncalibrated_fallback(self):
        from erh_core.core.judgement_system import ConservativeJudge
        judge = ConservativeJudge()
        action = Action(id=0, c=30, V=0.5, w=1.0)
        action.J = judge.judge(action)
        conf = judge.calibrated_confidence(action)
        expected = abs(action.J - action.V) / 2.0
        assert conf == pytest.approx(min(max(expected, 0.0), 1.0), abs=1e-6)


class TestAbstention:
    """Tests for judge_or_abstain() and evaluate_judgement(allow_abstention=True)."""

    def test_no_abstain_when_threshold_none(self):
        from erh_core.core.judgement_system import BiasedJudge
        judge = BiasedJudge()
        action = Action(id=0, c=50, V=0.3, w=1.0)
        result = judge.judge_or_abstain(action)
        assert result is not None

    def test_abstain_when_confidence_low(self):
        from erh_core.core.judgement_system import BiasedJudge
        judge = BiasedJudge(bias_strength=0.0, noise_scale=0.0)
        # With zero bias and zero noise J ≈ V, so |delta| ≈ 0, confidence ≈ 0
        action = Action(id=0, c=50, V=0.5, w=1.0)
        judge.set_abstention_threshold(0.9)  # high threshold
        result = judge.judge_or_abstain(action)
        # confidence ≈ 0 < 0.9 → should abstain
        assert result is None

    def test_evaluate_with_abstention_flag(self):
        from erh_core.core.judgement_system import BiasedJudge, evaluate_judgement
        from erh_core.core.action_space import generate_world
        judge = BiasedJudge(bias_strength=0.0, noise_scale=0.0)
        judge.set_abstention_threshold(0.99)  # almost all will abstain
        actions = generate_world(num_actions=20, random_seed=3)
        evaluate_judgement(actions, judge, tau=0.3, allow_abstention=True)
        abstained = [a for a in actions if a.J is None]
        # Some should have abstained
        assert len(abstained) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

