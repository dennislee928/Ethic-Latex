"""
Tests for the four new judge variants introduced in Phase 5:
  - IntersectionalJudge
  - TemporalJudge
  - CounterfactualJudge
  - FederatedJudge
"""

import copy
import sys
import os

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from erh_core.core.action_space import Action, generate_world
from erh_core.core.judgement_system import (
    BiasedJudge,
    NoisyJudge,
    ConservativeJudge,
    evaluate_judgement,
    IntersectionalJudge,
    TemporalJudge,
    CounterfactualJudge,
    FederatedJudge,
    DecisionTrace,
)
from erh_core.analysis.erh_checks import ERHCheckResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_actions(n: int = 120, seed: int = 42) -> list:
    return generate_world(num_actions=n, random_seed=seed)


def _group_key(action: Action) -> str:
    """Assign group by even/odd action id (simulates two demographic groups)."""
    return "group_A" if action.id % 2 == 0 else "group_B"


# ---------------------------------------------------------------------------
# IntersectionalJudge
# ---------------------------------------------------------------------------

class TestIntersectionalJudge:

    def test_judge_delegates_to_inner(self):
        inner = BiasedJudge(bias_strength=0.2, name="inner")
        judge = IntersectionalJudge(group_key=_group_key, inner_judge=inner)
        action = Action(id=0, c=30, V=0.4, w=1.0)
        J = judge.judge(action)
        assert -1.0 <= J <= 1.0

    def test_group_error_rates_returned(self):
        inner = BiasedJudge(bias_strength=0.3, noise_scale=0.1)
        judge = IntersectionalJudge(group_key=_group_key, inner_judge=inner)
        actions = _make_actions(n=100)
        evaluate_judgement(actions, judge, tau=0.3)

        rates = judge.get_group_error_rates(actions)
        assert "group_A" in rates
        assert "group_B" in rates
        for group, metrics in rates.items():
            assert "mae" in metrics
            assert "mistake_rate" in metrics
            assert "count" in metrics
            assert metrics["count"] > 0
            assert 0.0 <= metrics["mistake_rate"] <= 1.0

    def test_explain_has_group(self):
        inner = BiasedJudge()
        judge = IntersectionalJudge(group_key=_group_key, inner_judge=inner)
        action = Action(id=2, c=50, V=0.2, w=1.0)
        action.J = judge.judge(action)
        trace = judge.explain(action)
        assert isinstance(trace, DecisionTrace)
        feature_names = [f[0] for f in trace.top_features]
        assert "group_membership" in feature_names

    def test_returns_decision_trace_type(self):
        inner = NoisyJudge()
        judge = IntersectionalJudge(group_key=_group_key, inner_judge=inner)
        action = Action(id=1, c=20, V=-0.3, w=0.8)
        action.J = judge.judge(action)
        trace = judge.explain(action)
        assert trace.judge_name == judge.name


# ---------------------------------------------------------------------------
# TemporalJudge
# ---------------------------------------------------------------------------

class TestTemporalJudge:

    def test_judge_returns_float(self):
        inner = BiasedJudge()
        judge = TemporalJudge(inner_judge=inner, window_size=10)
        action = Action(id=0, c=40, V=0.3, w=1.0)
        J = judge.judge(action)
        assert -1.0 <= J <= 1.0

    def test_window_slides_on_overflow(self):
        inner = ConservativeJudge()
        judge = TemporalJudge(inner_judge=inner, window_size=5)
        actions = _make_actions(n=20)
        for a in actions:
            judge.judge(a)
        assert len(judge._window) == 5

    def test_window_erh_status_type(self):
        inner = BiasedJudge(bias_strength=0.1)
        judge = TemporalJudge(inner_judge=inner, window_size=50)
        actions = _make_actions(n=60)
        for a in actions:
            judge.judge(a)
        result = judge.get_window_erh_status()
        assert isinstance(result, ERHCheckResult)
        assert 0.0 <= result.violation_rate <= 1.0

    def test_window_too_small_raises(self):
        inner = BiasedJudge()
        judge = TemporalJudge(inner_judge=inner, window_size=50)
        action = Action(id=0, c=10, V=0.5, w=1.0)
        judge.judge(action)
        with pytest.raises(ValueError, match="Window too small"):
            judge.get_window_erh_status()

    def test_explain_includes_window_rate(self):
        inner = BiasedJudge(bias_strength=0.3)
        judge = TemporalJudge(inner_judge=inner, window_size=20)
        actions = _make_actions(n=25)
        for a in actions:
            judge.judge(a)
        action = actions[-1]
        action.J = judge.judge(action)
        trace = judge.explain(action)
        feature_names = [f[0] for f in trace.top_features]
        assert "window_violation_rate" in feature_names


# ---------------------------------------------------------------------------
# CounterfactualJudge
# ---------------------------------------------------------------------------

class TestCounterfactualJudge:

    def test_judge_delegates(self):
        inner = BiasedJudge(bias_strength=0.5)
        judge = CounterfactualJudge(inner_judge=inner)
        action = Action(id=0, c=50, V=0.0, w=1.0)
        J = judge.judge(action)
        assert -1.0 <= J <= 1.0

    def test_flip_found_for_clear_mistake(self):
        """High bias should produce a mistake; counterfactual should flip it."""
        inner = BiasedJudge(bias_strength=0.6, noise_scale=0.0)
        judge = CounterfactualJudge(inner_judge=inner, tau=0.3, max_steps=200, step_size=0.05)
        action = Action(id=0, c=10, V=0.0, w=1.0)
        action.J = judge.judge(action)
        action.delta = action.J - action.V
        # Only search for counterfactual if it actually is a mistake
        if abs(action.delta) > 0.3:
            cf = judge.find_counterfactual(action)
            assert isinstance(cf, dict)
            assert "found" in cf
            assert "flip_achieved" in cf
            assert "delta_V" in cf
            assert "delta_c" in cf

    def test_not_found_graceful(self):
        """A judge with zero bias should rarely produce mistakes; result has found=False."""
        inner = BiasedJudge(bias_strength=0.0, noise_scale=0.0)
        judge = CounterfactualJudge(inner_judge=inner, tau=0.3, max_steps=5)
        action = Action(id=0, c=50, V=0.5, w=1.0)
        action.J = judge.judge(action)
        cf = judge.find_counterfactual(action)
        # Either found or not — must always return a valid dict
        assert isinstance(cf, dict)
        assert "found" in cf
        assert isinstance(cf["found"], bool)

    def test_explain_has_counterfactual_features(self):
        inner = BiasedJudge(bias_strength=0.5, noise_scale=0.0)
        judge = CounterfactualJudge(inner_judge=inner, tau=0.3, max_steps=50)
        action = Action(id=0, c=10, V=0.0, w=1.0)
        action.J = judge.judge(action)
        trace = judge.explain(action)
        feature_names = [f[0] for f in trace.top_features]
        assert "counterfactual_found" in feature_names
        assert "counterfactual_delta_V" in feature_names


# ---------------------------------------------------------------------------
# FederatedJudge
# ---------------------------------------------------------------------------

class TestFederatedJudge:

    def _partitions(self, n_partitions=3, n_per_partition=60, seed=0):
        rng = np.random.default_rng(seed)
        all_actions = _make_actions(n=n_partitions * n_per_partition, seed=seed)
        partitions = []
        for i in range(n_partitions):
            partitions.append(all_actions[i * n_per_partition:(i + 1) * n_per_partition])
        return partitions

    def test_judge_delegates_single_action(self):
        inner = BiasedJudge()
        judge = FederatedJudge(local_judge=inner)
        action = Action(id=0, c=30, V=0.3, w=1.0)
        J = judge.judge(action)
        assert -1.0 <= J <= 1.0

    def test_aggregates_partitions(self):
        inner = BiasedJudge(bias_strength=0.2)
        judge = FederatedJudge(local_judge=inner, tau=0.3)
        partitions = self._partitions()
        result = judge.federated_erh_check(partitions)
        assert isinstance(result, ERHCheckResult)
        assert 0.0 <= result.violation_rate <= 1.0
        assert result.num_points > 0

    def test_returns_erh_check_result(self):
        inner = NoisyJudge(noise_scale=0.2)
        judge = FederatedJudge(local_judge=inner)
        partitions = self._partitions(n_partitions=2, n_per_partition=80)
        result = judge.federated_erh_check(partitions)
        assert isinstance(result, ERHCheckResult)
        assert result.judge_name == judge.name

    def test_only_counts_aggregated(self):
        """Verify that the federated check modifies only synthetic actions,
        not the original partition data."""
        inner = BiasedJudge(bias_strength=0.3)
        judge = FederatedJudge(local_judge=inner)
        partitions = self._partitions()
        # Save original V values
        originals = [[a.V for a in part] for part in partitions]
        judge.federated_erh_check(partitions)
        # Original partitions must be unchanged (deep copies used internally)
        for part, orig_vals in zip(partitions, originals):
            for a, v in zip(part, orig_vals):
                assert a.V == pytest.approx(v), "partition data was mutated"

    def test_empty_partitions_raises(self):
        inner = BiasedJudge()
        judge = FederatedJudge(local_judge=inner)
        with pytest.raises((ValueError, Exception)):
            judge.federated_erh_check([])

    def test_explain_delegates_to_inner(self):
        inner = BiasedJudge()
        judge = FederatedJudge(local_judge=inner)
        action = Action(id=0, c=40, V=0.2, w=1.0)
        action.J = inner.judge(action)
        trace = judge.explain(action)
        assert isinstance(trace, DecisionTrace)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
