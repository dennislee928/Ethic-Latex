"""
Unit tests for ERH Phase 1: LLM stress test and ethical primality.

Tests cover:
- scenario_generator: action_to_scenario_text, actions_to_prompts (no V revealed)
- ethical_primality_test: irreducibility at complexity x
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Project root on path for erh package
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erh.core.action_space import Action, generate_world
from erh.core.scenario_generator import (
    action_to_scenario_text,
    actions_to_prompts,
    DEFAULT_SYSTEM_PROMPT,
)
from erh.core.ethical_primes import ethical_primality_test


class TestScenarioGenerator:
    """Scenario text must not reveal ground truth V."""

    def test_action_to_scenario_text_minimal_no_v(self):
        action = Action(id=0, c=50, V=0.7, w=1.5)
        text = action_to_scenario_text(action, template="minimal")
        assert "0.7" not in text and "V" not in text
        assert "50" in text and "1.50" in text or "1.5" in text

    def test_action_to_scenario_text_narrative_no_v(self):
        action = Action(id=1, c=80, V=-0.5, w=2.0)
        text = action_to_scenario_text(action, template="narrative")
        assert "-0.5" not in text
        assert "80" in text or "highly complex" in text

    def test_actions_to_prompts_length(self):
        actions = generate_world(num_actions=5, random_seed=42)
        prompts = actions_to_prompts(actions, template="minimal")
        assert len(prompts) == 5
        for p in prompts:
            assert "action_id" in p and "user_content" in p and "system_prompt" in p
            assert p["system_prompt"] == DEFAULT_SYSTEM_PROMPT or len(p["system_prompt"]) > 0


class TestEthicalPrimalityTest:
    """ethical_primality_test(x, E_x, x_values) returns bool."""

    def test_returns_bool(self):
        E_x = np.array([0.1, 0.2, 0.5, 0.3, 0.2])
        x_vals = np.array([1, 2, 3, 4, 5])
        out = ethical_primality_test(5, E_x, x_vals)
        assert isinstance(out, bool)

    def test_insufficient_history_returns_true(self):
        E_x = np.array([0.1, 0.2])
        x_vals = np.array([1, 2])
        # x=2 has only 1 history point (min_history=3), so irreducible
        assert ethical_primality_test(2, E_x, x_vals) is True

    def test_empty_or_mismatched_returns_true(self):
        assert ethical_primality_test(3, np.array([]), np.array([])) is True
        assert ethical_primality_test(1, np.array([1.0]), np.array([1])) is True
