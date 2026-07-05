"""
Judgment System Module

This module defines various judge classes that evaluate moral actions,
introducing different types of biases, noise, and judgment strategies.
Supports HuggingFaceEthicalOracle for ground-truth V(a) from model scoring.

New in this version
-------------------
- DecisionTrace dataclass — structured record of each judgment decision
- BaseJudge.explain()   — per-judge feature attribution
- BaseJudge.calibrate() — Platt / isotonic confidence calibration
- BaseJudge.judge_or_abstain() — return None when confidence < threshold
- IntersectionalJudge   — per-group fairness evaluation
- TemporalJudge         — sliding-window ERH re-evaluation
- CounterfactualJudge   — minimal perturbation to flip a decision
- FederatedJudge        — privacy-preserving multi-partition ERH check
"""

import copy
import datetime
import logging
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .action_space import Action

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DecisionTrace — structured audit record for a single judgment
# ---------------------------------------------------------------------------

@dataclass
class DecisionTrace:
    """Audit record capturing why a judge reached a particular decision.

    Attributes
    ----------
    action_id : int
    judge_name : str
    J : float
        Judgment value in [-1, 1].
    V : float
        True moral value in [-1, 1].
    delta : float
        J - V.
    mistake_flag : int
        1 if `|delta|` > tau, else 0.
    top_features : List[Tuple[str, float]]
        Ordered list of (feature_name, contribution) pairs.
    reasoning : str
        Human-readable explanation of the decision.
    timestamp : str, optional
        ISO 8601 timestamp of when the trace was created.
    """
    action_id: int
    judge_name: str
    J: float
    V: float
    delta: float
    mistake_flag: int
    top_features: List[Tuple[str, float]]
    reasoning: str
    timestamp: Optional[str] = None


# ---------------------------------------------------------------------------
# BaseJudge — abstract base with calibration, abstention, and explainability
# ---------------------------------------------------------------------------

class BaseJudge(ABC):
    """Abstract base class for all judgment systems.

    A judge takes an action and produces a moral judgment J(a),
    which may differ from the true value V(a).

    Attributes
    ----------
    _calibrator : Any or None
        Fitted sklearn calibrator (None if uncalibrated).
    _calibration_method : str or None
        `"platt" | "isotonic" | None`.
    _decision_traces : list of DecisionTrace
        List of DecisionTrace objects (populated only when
        _store_traces is True).
    _store_traces : bool
        Toggle trace recording (default False).
    abstention_threshold : float or None
        When set, judge_or_abstain() returns None if
        calibrated_confidence() < threshold.
    """

    def __init__(self, name: str = "BaseJudge"):
        self.name = name
        self._calibrator: Optional[Any] = None
        self._calibration_method: Optional[str] = None
        self._decision_traces: List[DecisionTrace] = []
        self._store_traces: bool = False
        self.abstention_threshold: Optional[float] = None

    @abstractmethod
    def judge(self, action: Action) -> float:
        """Produce a judgment for the given action.

        Parameters
        ----------
        action : Action

        Returns
        -------
        float
            Judgment value J(a) in [-1, 1].
        """
        pass

    # ------------------------------------------------------------------
    # Explainability
    # ------------------------------------------------------------------

    def explain(self, action: Action) -> DecisionTrace:
        """Return a DecisionTrace explaining the judgment for *action*.

        The base implementation builds a generic trace from the judge's
        parameters and the action's features.  Concrete subclasses override
        this to provide class-specific feature attributions.

        If action.J is not yet set, judge() is called internally.
        """
        J = action.J if action.J is not None else self.judge(action)
        V = action.V
        delta = J - V
        tau = 0.3  # default; subclasses may use their own
        mistake_flag = 1 if abs(delta) > tau else 0

        top_features: List[Tuple[str, float]] = [
            ("true_value_V", float(V)),
            ("judgment_J", float(J)),
            ("error_delta", float(delta)),
            ("complexity_c", float(action.c)),
            ("importance_w", float(action.w)),
        ]
        reasoning = (
            f"{self.name} produced J={J:.3f} for action {action.id} "
            f"(V={V:.3f}, delta={delta:.3f}, "
            f"{'MISTAKE' if mistake_flag else 'correct'})"
        )
        ts = datetime.datetime.utcnow().isoformat()
        trace = DecisionTrace(
            action_id=action.id,
            judge_name=self.name,
            J=float(J),
            V=float(V),
            delta=float(delta),
            mistake_flag=mistake_flag,
            top_features=top_features,
            reasoning=reasoning,
            timestamp=ts,
        )
        if self._store_traces:
            self._decision_traces.append(trace)
        return trace

    def enable_trace_storage(self) -> None:
        """Enable automatic trace recording on every judge() call."""
        self._store_traces = True

    def disable_trace_storage(self) -> None:
        """Disable trace recording."""
        self._store_traces = False

    def get_traces(self) -> List[DecisionTrace]:
        """Return all stored DecisionTrace objects."""
        return list(self._decision_traces)

    def clear_traces(self) -> None:
        """Clear the stored trace list."""
        self._decision_traces.clear()

    # ------------------------------------------------------------------
    # Calibration
    # ------------------------------------------------------------------

    def calibrate(
        self,
        calibration_actions: List[Action],
        method: str = "platt",
    ) -> None:
        """Fit a calibrator to align confidence scores with violation rates.

        After calling calibrate(), calibrated_confidence() uses the fitted
        model rather than the raw `|delta|/2` proxy.

        Parameters
        ----------
        calibration_actions : List[Action]
            Actions that already have action.J and action.mistake_flag set.
        method : str
            "platt"    — LogisticRegression on `|delta|` scores.
            "isotonic" — IsotonicRegression on sorted `|delta|` scores.

        Raises
        ------
        ImportError
            If scikit-learn is not installed.
        ValueError
            If actions are missing required fields or only one class present.
        """
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.isotonic import IsotonicRegression
        except ImportError as exc:
            raise ImportError(
                "calibrate() requires scikit-learn. "
                "Install it with: pip install scikit-learn"
            ) from exc

        scores = []
        labels = []
        for a in calibration_actions:
            if a.delta is None or a.mistake_flag is None:
                continue
            scores.append(abs(a.delta))
            labels.append(int(a.mistake_flag))

        if len(scores) < 2:
            raise ValueError("Need at least 2 calibration actions with delta and mistake_flag set.")
        if len(set(labels)) < 2:
            raise ValueError(
                "Calibration requires both positive (mistake) and negative (correct) examples."
            )

        X = np.array(scores).reshape(-1, 1)
        y = np.array(labels)

        if method == "platt":
            clf = LogisticRegression(C=1.0, solver="lbfgs")
            clf.fit(X, y)
            self._calibrator = clf
        elif method == "isotonic":
            iso = IsotonicRegression(out_of_bounds="clip")
            # IsotonicRegression expects 1D input
            iso.fit(scores, y)
            self._calibrator = iso
        else:
            raise ValueError(f"Unknown calibration method: {method!r}. Use 'platt' or 'isotonic'.")

        self._calibration_method = method
        logger.info("Judge '%s' calibrated using %s on %d samples.", self.name, method, len(scores))

    def calibrated_confidence(self, action: Action) -> float:
        """Return P(violation) for *action*.

        Uses the fitted calibrator if available; otherwise falls back to
        `|J - V| / 2` as a raw unnormalised proxy (range 0–1).

        action.J must be set (or judge() is called internally to set it).
        """
        J = action.J if action.J is not None else self.judge(action)
        V = action.V
        delta_abs = abs(J - V)

        if self._calibrator is None:
            return float(np.clip(delta_abs / 2.0, 0.0, 1.0))

        if self._calibration_method == "platt":
            prob = self._calibrator.predict_proba([[delta_abs]])[0][1]
        else:  # isotonic
            prob = float(self._calibrator.predict([delta_abs])[0])

        return float(np.clip(prob, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Abstention
    # ------------------------------------------------------------------

    def set_abstention_threshold(self, threshold: float) -> None:
        """Set the confidence threshold below which the judge will abstain.

        Parameters
        ----------
        threshold : float
            Value in [0, 1].  When calibrated_confidence(action) < threshold,
            judge_or_abstain() returns None.
        """
        self.abstention_threshold = float(threshold)

    def judge_or_abstain(self, action: Action) -> Optional[float]:
        """Judge *action* or return None if confidence is below threshold.

        Returns
        -------
        float | None
            J(a) if confidence >= abstention_threshold (or threshold is None).
            None means the judge is uncertain and abstains.
        """
        J = self.judge(action)
        if self.abstention_threshold is None:
            return J
        conf = self.calibrated_confidence(action)
        if conf < self.abstention_threshold:
            return None
        return J

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


# ---------------------------------------------------------------------------
# Concrete judge implementations
# ---------------------------------------------------------------------------

class BiasedJudge(BaseJudge):
    """A judge with systematic bias that increases with complexity.

    This judge tends to systematically over- or under-estimate moral values,
    with the bias becoming stronger for more complex cases.

    Parameters
    ----------
    bias_strength : float, default=0.2
        Strength of the bias (positive = overestimate, negative = underestimate)
    noise_scale : float, default=0.1
        Standard deviation of random noise added to judgments
    complexity_dependency : float, default=0.5
        How much bias increases with complexity (0 = constant, 1 = linear)
    name : str, optional
        Name for this judge

    Examples
    --------
    >>> judge = BiasedJudge(bias_strength=0.3, noise_scale=0.1)
    >>> action = Action(id=0, c=50, V=0.5, w=1.0)
    >>> judgment = judge.judge(action)
    """

    def __init__(
        self,
        bias_strength: float = 0.2,
        noise_scale: float = 0.1,
        complexity_dependency: float = 0.5,
        name: str = "BiasedJudge"
    ):
        super().__init__(name)
        self.bias_strength = bias_strength
        self.noise_scale = noise_scale
        self.complexity_dependency = complexity_dependency

    def judge(self, action: Action) -> float:
        """Judge with complexity-dependent bias.

        J(a) = V(a) + bias * f(c) + noise
        where f(c) is a function of complexity
        """
        c_normalized = action.c / 100.0
        bias_factor = 1 + self.complexity_dependency * c_normalized
        bias = self.bias_strength * bias_factor
        noise = np.random.normal(0, self.noise_scale)
        J = action.V + bias + noise
        return float(np.clip(J, -1, 1))

    def explain(self, action: Action) -> DecisionTrace:
        J = action.J if action.J is not None else self.judge(action)
        V = action.V
        delta = J - V
        c_normalized = action.c / 100.0
        bias_factor = 1 + self.complexity_dependency * c_normalized
        bias_contribution = self.bias_strength * bias_factor
        noise_contribution = delta - bias_contribution
        mistake_flag = 1 if abs(delta) > 0.3 else 0

        top_features = [
            ("bias_strength", float(self.bias_strength)),
            ("complexity_bias_contribution", float(bias_contribution)),
            ("noise_contribution", float(noise_contribution)),
            ("complexity_c", float(action.c)),
            ("true_value_V", float(V)),
        ]
        reasoning = (
            f"BiasedJudge '{self.name}': bias={bias_contribution:.3f} (strength={self.bias_strength}, "
            f"c={action.c}), noise≈{noise_contribution:.3f}, delta={delta:.3f}"
        )
        ts = datetime.datetime.utcnow().isoformat()
        trace = DecisionTrace(
            action_id=action.id, judge_name=self.name,
            J=float(J), V=float(V), delta=float(delta),
            mistake_flag=mistake_flag, top_features=top_features,
            reasoning=reasoning, timestamp=ts,
        )
        if self._store_traces:
            self._decision_traces.append(trace)
        return trace


class NoisyJudge(BaseJudge):
    """A judge with high random noise but no systematic bias.

    Parameters
    ----------
    noise_scale : float, default=0.3
        Standard deviation of the judgment noise
    complexity_scaling : bool, default=True
        If True, noise increases with complexity
    name : str, optional
    """

    def __init__(
        self,
        noise_scale: float = 0.3,
        complexity_scaling: bool = True,
        name: str = "NoisyJudge"
    ):
        super().__init__(name)
        self.noise_scale = noise_scale
        self.complexity_scaling = complexity_scaling

    def judge(self, action: Action) -> float:
        if self.complexity_scaling:
            c_normalized = action.c / 100.0
            effective_noise = self.noise_scale * (1 + c_normalized)
        else:
            effective_noise = self.noise_scale
        noise = np.random.normal(0, effective_noise)
        J = action.V + noise
        return float(np.clip(J, -1, 1))

    def explain(self, action: Action) -> DecisionTrace:
        J = action.J if action.J is not None else self.judge(action)
        V = action.V
        delta = J - V
        c_normalized = action.c / 100.0
        eff = self.noise_scale * (1 + c_normalized) if self.complexity_scaling else self.noise_scale
        mistake_flag = 1 if abs(delta) > 0.3 else 0

        top_features = [
            ("noise_scale", float(self.noise_scale)),
            ("effective_noise_at_c", float(eff)),
            ("complexity_scaling_enabled", float(self.complexity_scaling)),
            ("complexity_c", float(action.c)),
            ("true_value_V", float(V)),
        ]
        reasoning = (
            f"NoisyJudge '{self.name}': effective_noise={eff:.3f} at c={action.c}, "
            f"delta={delta:.3f}"
        )
        ts = datetime.datetime.utcnow().isoformat()
        trace = DecisionTrace(
            action_id=action.id, judge_name=self.name,
            J=float(J), V=float(V), delta=float(delta),
            mistake_flag=mistake_flag, top_features=top_features,
            reasoning=reasoning, timestamp=ts,
        )
        if self._store_traces:
            self._decision_traces.append(trace)
        return trace


class ConservativeJudge(BaseJudge):
    """A conservative judge that tends toward neutral (0) judgments.

    Parameters
    ----------
    threshold : float, default=0.5
        How strongly to pull toward neutral (0 = no effect, 1 = always neutral)
    noise_scale : float, default=0.1
        Random noise
    complexity_dependency : float, default=0.7
        How much conservatism increases with complexity
    name : str, optional
    """

    def __init__(
        self,
        threshold: float = 0.5,
        noise_scale: float = 0.1,
        complexity_dependency: float = 0.7,
        name: str = "ConservativeJudge"
    ):
        super().__init__(name)
        self.threshold = threshold
        self.noise_scale = noise_scale
        self.complexity_dependency = complexity_dependency

    def judge(self, action: Action) -> float:
        c_normalized = action.c / 100.0
        conservatism = self.threshold * (1 + self.complexity_dependency * c_normalized)
        conservatism = np.clip(conservatism, 0, 1)
        J = (1 - conservatism) * action.V + conservatism * 0
        noise = np.random.normal(0, self.noise_scale)
        J += noise
        return float(np.clip(J, -1, 1))

    def explain(self, action: Action) -> DecisionTrace:
        J = action.J if action.J is not None else self.judge(action)
        V = action.V
        delta = J - V
        c_normalized = action.c / 100.0
        conservatism = float(np.clip(
            self.threshold * (1 + self.complexity_dependency * c_normalized), 0, 1
        ))
        mistake_flag = 1 if abs(delta) > 0.3 else 0

        top_features = [
            ("conservatism_level", conservatism),
            ("pull_toward_neutral", conservatism * abs(V)),
            ("threshold", float(self.threshold)),
            ("complexity_c", float(action.c)),
            ("true_value_V", float(V)),
        ]
        reasoning = (
            f"ConservativeJudge '{self.name}': conservatism={conservatism:.3f} at c={action.c}, "
            f"pulls toward 0 — delta={delta:.3f}"
        )
        ts = datetime.datetime.utcnow().isoformat()
        trace = DecisionTrace(
            action_id=action.id, judge_name=self.name,
            J=float(J), V=float(V), delta=float(delta),
            mistake_flag=mistake_flag, top_features=top_features,
            reasoning=reasoning, timestamp=ts,
        )
        if self._store_traces:
            self._decision_traces.append(trace)
        return trace


class RadicalJudge(BaseJudge):
    """A radical judge that amplifies extremes and avoids neutral judgments.

    Parameters
    ----------
    amplification : float, default=1.5
        Factor by which to amplify judgments (>1)
    noise_scale : float, default=0.1
        Random noise
    name : str, optional
    """

    def __init__(
        self,
        amplification: float = 1.5,
        noise_scale: float = 0.1,
        name: str = "RadicalJudge"
    ):
        super().__init__(name)
        self.amplification = amplification
        self.noise_scale = noise_scale

    def judge(self, action: Action) -> float:
        J = action.V * self.amplification
        noise = np.random.normal(0, self.noise_scale)
        J += noise
        return float(np.clip(J, -1, 1))

    def explain(self, action: Action) -> DecisionTrace:
        J = action.J if action.J is not None else self.judge(action)
        V = action.V
        delta = J - V
        amplification_effect = V * (self.amplification - 1.0)
        mistake_flag = 1 if abs(delta) > 0.3 else 0

        top_features = [
            ("amplification_factor", float(self.amplification)),
            ("amplification_effect", float(amplification_effect)),
            ("noise_scale", float(self.noise_scale)),
            ("true_value_V", float(V)),
        ]
        reasoning = (
            f"RadicalJudge '{self.name}': amplification={self.amplification}×, "
            f"amplified by {amplification_effect:.3f} — delta={delta:.3f}"
        )
        ts = datetime.datetime.utcnow().isoformat()
        trace = DecisionTrace(
            action_id=action.id, judge_name=self.name,
            J=float(J), V=float(V), delta=float(delta),
            mistake_flag=mistake_flag, top_features=top_features,
            reasoning=reasoning, timestamp=ts,
        )
        if self._store_traces:
            self._decision_traces.append(trace)
        return trace


class OracleDrivenJudge(BaseJudge):
    """Judge that sets V(a) from HuggingFaceEthicalOracle before computing J(a).

    Supports GroundTruthProxy priority: if csv_proxy has action_id, use it;
    else use oracle.score(action.description). E(x) = `|J - V|`.

    Parameters
    ----------
    oracle : HuggingFaceEthicalOracle
    inner_judge : BaseJudge, optional
    csv_proxy : Any, optional
    name : str, optional
    """

    def __init__(
        self,
        oracle: Any,
        inner_judge: Optional["BaseJudge"] = None,
        csv_proxy: Optional[Any] = None,
        name: str = "OracleDrivenJudge",
    ):
        super().__init__(name)
        self.oracle = oracle
        self.inner_judge = inner_judge
        self.csv_proxy = csv_proxy

    def _get_V(self, action: Action) -> float:
        if self.csv_proxy is not None and hasattr(self.csv_proxy, "_data"):
            if action.id in self.csv_proxy._data:
                return self.csv_proxy.get_V(action)
        text = getattr(action, "description", None) or ""
        if text:
            return self.oracle.score(text)
        return action.V

    def judge(self, action: Action) -> float:
        action.V = self._get_V(action)
        if self.inner_judge is not None:
            return self.inner_judge.judge(action)
        return action.V


class CustomJudge(BaseJudge):
    """A judge with a custom judgment function.

    Parameters
    ----------
    judge_func : Callable[[Action], float]
    name : str, optional
    """

    def __init__(
        self,
        judge_func: Callable[[Action], float],
        name: str = "CustomJudge"
    ):
        super().__init__(name)
        self.judge_func = judge_func

    def judge(self, action: Action) -> float:
        return self.judge_func(action)


# ---------------------------------------------------------------------------
# New judge variants
# ---------------------------------------------------------------------------

class IntersectionalJudge(BaseJudge):
    """Evaluates intersectional fairness across demographic sub-groups.

    Parameters
    ----------
    group_key : Callable[[Action], str]
        Maps an action to its demographic group label, e.g.
        ``lambda a: f"{a.race}_{a.gender}"``.  The Action attributes used
        must exist on the action objects being judged.
    inner_judge : BaseJudge
        The underlying judge that produces J(a).
    name : str
    """

    def __init__(
        self,
        group_key: Callable[[Action], str],
        inner_judge: BaseJudge,
        name: str = "IntersectionalJudge",
    ):
        super().__init__(name)
        self.group_key = group_key
        self.inner_judge = inner_judge

    def judge(self, action: Action) -> float:
        return self.inner_judge.judge(action)

    def get_group_error_rates(
        self,
        actions: List[Action],
    ) -> Dict[str, Dict[str, float]]:
        """Compute per-group error metrics from already-judged actions.

        Parameters
        ----------
        actions : List[Action]
            Actions that have action.J, action.delta, action.mistake_flag set.

        Returns
        -------
        Dict[str, Dict[str, float]]
            {group_label: {mae, mistake_rate, count}}
        """
        groups: Dict[str, List[Action]] = {}
        for a in actions:
            if a.delta is None or a.mistake_flag is None:
                continue
            key = self.group_key(a)
            groups.setdefault(key, []).append(a)

        result = {}
        for key, acts in groups.items():
            deltas = [abs(a.delta) for a in acts]
            flags = [a.mistake_flag for a in acts]
            result[key] = {
                "mae": float(np.mean(deltas)),
                "mistake_rate": float(np.mean(flags)),
                "count": float(len(acts)),
            }
        return result

    def explain(self, action: Action) -> DecisionTrace:
        J = action.J if action.J is not None else self.judge(action)
        V = action.V
        delta = J - V
        group = self.group_key(action)
        mistake_flag = 1 if abs(delta) > 0.3 else 0

        top_features = [
            ("group_membership", 1.0),
            ("group_label_encoded", float(hash(group) % 1000) / 1000),
            ("true_value_V", float(V)),
            ("judgment_J", float(J)),
            ("error_delta", float(delta)),
        ]
        reasoning = (
            f"IntersectionalJudge '{self.name}': group='{group}', "
            f"J={J:.3f}, V={V:.3f}, delta={delta:.3f}"
        )
        ts = datetime.datetime.utcnow().isoformat()
        trace = DecisionTrace(
            action_id=action.id, judge_name=self.name,
            J=float(J), V=float(V), delta=float(delta),
            mistake_flag=mistake_flag, top_features=top_features,
            reasoning=reasoning, timestamp=ts,
        )
        if self._store_traces:
            self._decision_traces.append(trace)
        return trace


class TemporalJudge(BaseJudge):
    """Sliding-window judge that re-evaluates the ERH bound incrementally.

    Designed for streaming / online settings.  Each call to judge() adds the
    action to an internal fixed-size deque.  Call get_window_erh_status() at
    any time to compute the ERH bound over the current window.

    Parameters
    ----------
    inner_judge : BaseJudge
    window_size : int, default=100
    erh_C : float
    erh_epsilon : float
    name : str
    """

    def __init__(
        self,
        inner_judge: BaseJudge,
        window_size: int = 100,
        erh_C: float = 1.0,
        erh_epsilon: float = 0.1,
        name: str = "TemporalJudge",
    ):
        super().__init__(name)
        self.inner_judge = inner_judge
        self.window_size = window_size
        self.erh_C = erh_C
        self.erh_epsilon = erh_epsilon
        self._window: deque = deque(maxlen=window_size)

    def judge(self, action: Action) -> float:
        J = self.inner_judge.judge(action)
        # Store a copy so window actions are independent of external mutations
        a_copy = copy.deepcopy(action)
        a_copy.J = J
        a_copy.delta = J - action.V
        a_copy.mistake_flag = 1 if abs(a_copy.delta) > 0.3 else 0
        self._window.append(a_copy)
        return J

    def get_window_erh_status(self) -> "ERHCheckResult":
        """Compute ERH bound over the current sliding window.

        Returns
        -------
        ERHCheckResult
            Populated with judge_name and current window statistics.

        Raises
        ------
        ValueError
            If the window contains fewer than 2 distinct complexity values.
        """
        # Lazy import avoids circular dependency
        from erh_core.core.ethical_primes import select_ethical_primes, compute_Pi_and_error
        from erh_core.analysis.erh_checks import check_erh_bound_structured

        window_actions = list(self._window)
        if len(window_actions) < 2:
            raise ValueError("Window too small to compute ERH status (need ≥ 2 actions).")

        primes = select_ethical_primes(window_actions)
        x_max = max(2, int(np.ceil(max(a.c for a in window_actions))))
        _Pi_x, _B_x, E_x, x_values = compute_Pi_and_error(primes, X_max=x_max)

        if len(x_values) == 0:
            raise ValueError("No valid ERH data points in current window.")

        result = check_erh_bound_structured(
            E_x, x_values,
            C=self.erh_C,
            epsilon=self.erh_epsilon,
            judge_name=self.name,
        )
        return result

    def explain(self, action: Action) -> DecisionTrace:
        J = action.J if action.J is not None else self.judge(action)
        V = action.V
        delta = J - V
        window_violation_rate = (
            float(np.mean([a.mistake_flag for a in self._window if a.mistake_flag is not None]))
            if self._window else 0.0
        )
        mistake_flag = 1 if abs(delta) > 0.3 else 0

        top_features = [
            ("window_violation_rate", window_violation_rate),
            ("window_size_current", float(len(self._window))),
            ("window_size_max", float(self.window_size)),
            ("error_delta", float(delta)),
            ("complexity_c", float(action.c)),
        ]
        reasoning = (
            f"TemporalJudge '{self.name}': window_violation_rate={window_violation_rate:.3f} "
            f"(n={len(self._window)}), delta={delta:.3f}"
        )
        ts = datetime.datetime.utcnow().isoformat()
        trace = DecisionTrace(
            action_id=action.id, judge_name=self.name,
            J=float(J), V=float(V), delta=float(delta),
            mistake_flag=mistake_flag, top_features=top_features,
            reasoning=reasoning, timestamp=ts,
        )
        if self._store_traces:
            self._decision_traces.append(trace)
        return trace


class CounterfactualJudge(BaseJudge):
    """Generates minimal feature perturbations that flip a judge's decision.

    For a flagged action (mistake_flag=1), find the smallest change to
    action.c and action.V such that the judge would no longer flag it.

    Uses a gradient-free grid search — no external ML dependencies required.

    Parameters
    ----------
    inner_judge : BaseJudge
    tau : float, default=0.3
        Mistake threshold.
    max_steps : int, default=50
        Maximum L1-distance steps before giving up.
    step_size : float, default=0.05
        Perturbation step size for action.V.
    name : str
    """

    def __init__(
        self,
        inner_judge: BaseJudge,
        tau: float = 0.3,
        max_steps: int = 50,
        step_size: float = 0.05,
        name: str = "CounterfactualJudge",
    ):
        super().__init__(name)
        self.inner_judge = inner_judge
        self.tau = tau
        self.max_steps = max_steps
        self.step_size = step_size

    def judge(self, action: Action) -> float:
        return self.inner_judge.judge(action)

    def find_counterfactual(self, action: Action) -> Dict[str, Any]:
        """Find the minimal (delta_c, delta_V) that flips the mistake flag.

        The search iterates over (delta_V, delta_c) pairs in ascending L1
        order, re-calling inner_judge.judge() after each perturbation.

        Parameters
        ----------
        action : Action
            Should have action.J set (or it is computed internally).

        Returns
        -------
        dict with keys:
            found          bool — whether a flip was found within max_steps
            steps          int  — number of perturbation steps tried
            delta_c        float — complexity offset (integer-rounded)
            delta_V        float — moral value offset
            perturbed_J    float — J after perturbation
            flip_achieved  bool — synonym for found
        """
        J_orig = action.J if action.J is not None else self.inner_judge.judge(action)
        mistake_orig = 1 if abs(J_orig - action.V) > self.tau else 0

        steps = 0
        # Build candidate perturbations sorted by L1 distance
        v_range = np.arange(-1.0, 1.0 + self.step_size, self.step_size)
        c_range_raw = np.arange(-10, 11, 1)  # integer complexity offsets

        candidates = sorted(
            [(dv, dc) for dv in v_range for dc in c_range_raw],
            key=lambda pair: abs(pair[0]) + abs(pair[1]),
        )

        for dv, dc in candidates:
            if steps >= self.max_steps:
                break
            steps += 1

            perturbed = copy.deepcopy(action)
            perturbed.V = float(np.clip(action.V + dv, -1, 1))
            perturbed.c = max(1, int(action.c + dc))

            J_new = self.inner_judge.judge(perturbed)
            mistake_new = 1 if abs(J_new - perturbed.V) > self.tau else 0

            if mistake_new != mistake_orig:
                return {
                    "found": True,
                    "steps": steps,
                    "delta_c": float(dc),
                    "delta_V": float(dv),
                    "perturbed_J": float(J_new),
                    "flip_achieved": True,
                }

        return {
            "found": False,
            "steps": steps,
            "delta_c": 0.0,
            "delta_V": 0.0,
            "perturbed_J": float(J_orig),
            "flip_achieved": False,
        }

    def explain(self, action: Action) -> DecisionTrace:
        J = action.J if action.J is not None else self.judge(action)
        V = action.V
        delta = J - V
        mistake_flag = 1 if abs(delta) > self.tau else 0

        cf = self.find_counterfactual(action) if mistake_flag else {
            "found": False, "delta_c": 0.0, "delta_V": 0.0
        }

        top_features = [
            ("error_delta", float(delta)),
            ("counterfactual_found", float(cf["found"])),
            ("counterfactual_delta_V", float(cf["delta_V"])),
            ("counterfactual_delta_c", float(cf["delta_c"])),
            ("complexity_c", float(action.c)),
        ]
        cf_str = (
            f"flip via delta_V={cf['delta_V']:.3f}, delta_c={cf['delta_c']}"
            if cf["found"] else "no flip found within max_steps"
        )
        reasoning = (
            f"CounterfactualJudge '{self.name}': delta={delta:.3f} — {cf_str}"
        )
        ts = datetime.datetime.utcnow().isoformat()
        trace = DecisionTrace(
            action_id=action.id, judge_name=self.name,
            J=float(J), V=float(V), delta=float(delta),
            mistake_flag=mistake_flag, top_features=top_features,
            reasoning=reasoning, timestamp=ts,
        )
        if self._store_traces:
            self._decision_traces.append(trace)
        return trace


class FederatedJudge(BaseJudge):
    """Privacy-preserving federated judging across multiple data partitions.

    Runs the judge locally on each partition and aggregates only violation
    counts (not raw action data) to compute a global ERH bound.

    No network I/O — operates on a list of pre-partitioned action lists.

    Parameters
    ----------
    local_judge : BaseJudge
        Judge applied to every partition.
    tau : float, default=0.3
    name : str
    """

    def __init__(
        self,
        local_judge: BaseJudge,
        tau: float = 0.3,
        name: str = "FederatedJudge",
    ):
        super().__init__(name)
        self.local_judge = local_judge
        self.tau = tau

    def judge(self, action: Action) -> float:
        return self.local_judge.judge(action)

    def federated_erh_check(
        self,
        partitions: List[List[Action]],
        C: float = 1.0,
        epsilon: float = 0.1,
        slack_factor: float = 1.5,
        allowed_violation_rate: float = 0.05,
    ) -> "ERHCheckResult":
        """Aggregate violation counts across partitions and check the global ERH bound.

        Privacy model
        -------------
        Only per-complexity mistake *counts* cross partition boundaries.
        Raw action data (V, J, delta, description) never leaves its partition.

        Parameters
        ----------
        partitions : List[List[Action]]
            Each inner list is one private data partition.

        Returns
        -------
        ERHCheckResult
            Global result computed from aggregated counts.
        """
        from erh_core.core.ethical_primes import select_ethical_primes, compute_Pi_and_error
        from erh_core.analysis.erh_checks import check_erh_bound_structured

        # Aggregate per-complexity mistake counts across partitions
        # Keys: complexity value (int), Values: (mistake_count, total_count)
        global_counts: Dict[int, Tuple[int, int]] = {}

        for partition in partitions:
            local = copy.deepcopy(partition)
            evaluate_judgement(local, self.local_judge, tau=self.tau, inplace=True)

            for a in local:
                if a.mistake_flag is None:
                    continue
                c_key = int(a.c)
                prev_m, prev_t = global_counts.get(c_key, (0, 0))
                global_counts[c_key] = (prev_m + int(a.mistake_flag), prev_t + 1)

        if not global_counts:
            raise ValueError("No valid actions across all partitions.")

        # Reconstruct synthetic actions from counts for the ethical_primes pipeline
        synthetic_actions: List[Action] = []
        action_id = 0
        for c_val, (mistake_cnt, total_cnt) in sorted(global_counts.items()):
            for _ in range(total_cnt):
                V = 0.5  # neutral placeholder — only mistake_flag matters for E(x)
                J = (V + self.tau + 0.01) if action_id < mistake_cnt else V
                a = Action(id=action_id, c=c_val, V=V, w=1.0)
                a.J = J
                a.delta = J - V
                a.mistake_flag = 1 if action_id < mistake_cnt else 0
                synthetic_actions.append(a)
                action_id += 1

        primes = select_ethical_primes(synthetic_actions)
        x_max = max(2, int(max(global_counts.keys())))
        _Pi_x, _B_x, E_x, x_values = compute_Pi_and_error(primes, X_max=x_max)

        if len(x_values) == 0:
            raise ValueError("No valid ERH data points after aggregating partitions.")

        return check_erh_bound_structured(
            E_x, x_values,
            C=C, epsilon=epsilon,
            slack_factor=slack_factor,
            allowed_violation_rate=allowed_violation_rate,
            judge_name=self.name,
        )

    def explain(self, action: Action) -> DecisionTrace:
        return self.local_judge.explain(action)


# ---------------------------------------------------------------------------
# Evaluation utilities (unchanged signatures — backward compatible)
# ---------------------------------------------------------------------------

def evaluate_judgement(
    actions: List[Action],
    judge: BaseJudge,
    tau: float = 0.3,
    inplace: bool = True,
    allow_abstention: bool = False,
) -> Optional[List[Action]]:
    """Evaluate all actions with a given judge and compute errors.

    Supports multidimensional moral values if Action.V_vector is present.

    Parameters
    ----------
    actions : List[Action]
    judge : BaseJudge
    tau : float, default=0.3
    inplace : bool, default=True
    allow_abstention : bool, default=False

    Returns
    -------
    Optional[List[Action]]
        None if inplace=True; copy of evaluated actions if inplace=False.
    """
    if not inplace:
        actions = copy.deepcopy(actions)

    for action in actions:
        if allow_abstention:
            J = judge.judge_or_abstain(action)
        else:
            J = judge.judge(action)

        if J is None:
            # Abstention — mark as uncertain
            action.J = None
            action.delta = None
            action.mistake_flag = None
            action.J_vector = None
            action.delta_vector = None
        else:
            action.J = J
            action.delta = J - action.V
            
            # Handle multidimensional values if present
            if action.V_vector is not None:
                # For Multi-dimensional Zeta, we simulate multi-dim judgment
                # by adding small independent noise to each dimension of V
                noise = np.random.normal(0, abs(action.delta) * 0.5, len(action.V_vector))
                action.J_vector = action.V_vector + (J - action.V) + noise
                action.delta_vector = action.J_vector - action.V_vector
                
                # Mistake flag is 1 if any dimension exceeds tau or if scalar delta exceeds tau
                # (Formalizing ethical phase transition as any dimension collapsing)
                max_dim_delta = np.max(np.abs(action.delta_vector))
                action.mistake_flag = 1 if (abs(action.delta) > tau or max_dim_delta > tau) else 0
            else:
                action.mistake_flag = 1 if abs(action.delta) > tau else 0

        if getattr(judge, '_store_traces', False) and J is not None:
            judge._decision_traces.append(judge.explain(action))

    if not inplace:
        return actions


def batch_evaluate(
    actions: List[Action],
    judges: dict,
    tau: float = 0.3
) -> dict:
    """Evaluate actions with multiple judges.

    Parameters
    ----------
    actions : List[Action]
    judges : dict
        {judge_name: BaseJudge}
    tau : float

    Returns
    -------
    dict
        {judge_name: [evaluated_actions]}

    Examples
    --------
    >>> judges = {'biased': BiasedJudge(), 'noisy': NoisyJudge()}
    >>> results = batch_evaluate(actions, judges)
    """
    results = {}
    for name, judge in judges.items():
        actions_copy = copy.deepcopy(actions)
        evaluate_judgement(actions_copy, judge, tau=tau, inplace=True)
        results[name] = actions_copy
    return results


def compute_judgment_metrics(actions: List[Action]) -> dict:
    """Compute various metrics about judgment quality.

    Parameters
    ----------
    actions : List[Action]
        Actions with judgments set.

    Returns
    -------
    dict
        mae, rmse, mean_error, std_error, max_error, mistake_count,
        mistake_rate, total_actions.
    """
    deltas = [a.delta for a in actions if a.delta is not None]
    mistakes = [a.mistake_flag for a in actions if a.mistake_flag is not None]

    if not deltas:
        return {}

    return {
        'mae': float(np.mean(np.abs(deltas))),
        'rmse': float(np.sqrt(np.mean(np.array(deltas) ** 2))),
        'mean_error': float(np.mean(deltas)),
        'std_error': float(np.std(deltas)),
        'max_error': float(np.max(np.abs(deltas))),
        'mistake_count': int(sum(mistakes)),
        'mistake_rate': float(np.mean(mistakes)),
        'total_actions': len(actions),
    }
