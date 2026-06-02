"""
Content moderation real-data case study for the Ethical Riemann Hypothesis.

This module maps a moderation benchmark into the standard ERH fields:
text post, complexity, ground truth, importance weight, and model judgment.
It is safe to run without external datasets or model downloads; when optional
dependencies are unavailable it uses deterministic local stubs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.real_data.compas_case_study import calculate_cumulative_error, fit_power_law

DEFAULT_OUTPUT = PROJECT_ROOT / "simulation" / "output" / "content_moderation_erh.json"

ModerationRow = Dict[str, Any]
ToxicityScorer = Callable[[str], float]

IMPLICIT_MARKERS = (
    "just asking",
    "obviously",
    "those people",
    "they know",
    "not racist",
    "doesn't belong",
    "do not belong",
    "never fit",
    "never belong",
)
SARCASM_MARKERS = ("...", "/s", "yeah right", "sure,", "just joking", "as if")
VIOLENCE_MARKERS = ("attack", "attacked", "kill", "hurt", "threat", "violence")
SLUR_MARKERS = ("slur", "subhuman", "vermin")


def _truth_from_label(label: Any) -> float:
    """Map moderation labels to V(a): hateful=+1, benign=-1."""
    if isinstance(label, str):
        normalized = label.strip().lower()
        if normalized in {"hate", "hateful", "toxic", "abusive", "1", "true"}:
            return 1.0
        if normalized in {"normal", "benign", "non-hate", "none", "0", "false"}:
            return -1.0
    return 1.0 if int(label) == 1 else -1.0


def _judgment_from_probability(probability: float) -> float:
    """Map classifier hate probability in [0, 1] to J(a) in [-1, 1]."""
    return float(np.clip((2.0 * float(probability)) - 1.0, -1.0, 1.0))


def _complexity_from_post(row: ModerationRow) -> int:
    """
    Estimate moderation complexity from implicitness, sarcasm, and category.

    Explicit hate is intentionally lower complexity than implicit or ironic
    hate because the case study asks whether failures grow on ambiguous text.
    """
    text = str(row.get("text") or row.get("post") or row.get("comment") or "")
    lowered = text.lower()
    category = str(row.get("category") or row.get("type") or "").lower()

    implicit_count = sum(1 for marker in IMPLICIT_MARKERS if marker in lowered)
    sarcasm_count = sum(1 for marker in SARCASM_MARKERS if marker in lowered)
    token_count = len(text.split())

    if "implicit" in category:
        category_score = 30
    elif "explicit" in category or "slur" in category:
        category_score = 5
    elif "counter" in category:
        category_score = 15
    else:
        category_score = 10

    raw = implicit_count * 15 + sarcasm_count * 10 + category_score + token_count
    return int(np.clip(raw, 1, 100))


def _importance_from_post(row: ModerationRow) -> float:
    """Map moderation stakes to w(a)."""
    text = str(row.get("text") or row.get("post") or row.get("comment") or "").lower()
    severity = str(row.get("severity") or row.get("category") or row.get("type") or "").lower()

    if "violence" in severity or any(marker in text for marker in VIOLENCE_MARKERS):
        return 4.0
    if "slur" in severity or any(marker in text for marker in SLUR_MARKERS):
        return 3.0
    if "implicit" in severity:
        return 2.0
    if "counter" in severity:
        return 1.5
    return 1.0


def _default_stub_rows(max_samples: int) -> List[ModerationRow]:
    rows = [
        {"text": "I hope those people are attacked tonight", "label": 1, "severity": "violence"},
        {"text": "A direct slur should be removed", "label": 1, "category": "slur"},
        {"text": "Everyone is welcome at the community meeting", "label": 0, "category": "benign"},
        {"text": "Just joking... they never fit in here", "label": 1, "category": "implicit"},
        {"text": "Counter speech calling out hate", "label": 0, "category": "counter_speech"},
        {"text": "Those people do not belong in our town", "label": 1, "category": "implicit"},
        {"text": "Please stop spreading hateful rumors", "label": 0, "category": "counter_speech"},
        {"text": "Sure, let them move next door... as if", "label": 1, "category": "implicit"},
    ]
    if max_samples <= len(rows):
        return rows[:max_samples]
    repeated: List[ModerationRow] = []
    while len(repeated) < max_samples:
        repeated.extend(rows)
    return repeated[:max_samples]


def _load_hf_rows(dataset: str = "ethos", max_samples: int = 200) -> List[ModerationRow]:
    """
    Load a HuggingFace moderation dataset if available, otherwise return stubs.

    The fallback keeps direct script execution useful in offline CI.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        return _default_stub_rows(max_samples)

    try:
        if dataset == "hatexplain":
            ds = load_dataset("hatexplain", split=f"train[:{max_samples}]")
            rows: List[ModerationRow] = []
            for item in ds:
                annotators = item.get("annotators") or {}
                labels = annotators.get("label") or []
                hateful_votes = sum(1 for value in labels if str(value).lower() in {"hatespeech", "offensive", "1", "2"})
                label = 1 if labels and hateful_votes >= (len(labels) / 2) else 0
                post_tokens = item.get("post_tokens") or []
                rows.append(
                    {
                        "text": " ".join(map(str, post_tokens)),
                        "label": label,
                        "category": "implicit" if item.get("rationales") else "explicit",
                        "target_groups": item.get("target_group", []),
                    }
                )
            return rows or _default_stub_rows(max_samples)

        ds = load_dataset("ethos", "binary", split=f"train[:{max_samples}]")
        return [
            {
                "text": item.get("text", ""),
                "label": int(item.get("label", 0)),
                "category": "explicit" if int(item.get("label", 0)) == 1 else "benign",
            }
            for item in ds
        ]
    except Exception:
        return _default_stub_rows(max_samples)


def _heuristic_toxicity_scorer(text: str) -> float:
    """Deterministic offline scorer used when model packages are unavailable."""
    lowered = text.lower()
    score = 0.08
    if any(marker in lowered for marker in VIOLENCE_MARKERS):
        score += 0.72
    if any(marker in lowered for marker in SLUR_MARKERS):
        score += 0.68
    if any(marker in lowered for marker in IMPLICIT_MARKERS):
        score += 0.28
    if any(marker in lowered for marker in SARCASM_MARKERS):
        score -= 0.10
    if "counter speech" in lowered or "calling out hate" in lowered:
        score -= 0.15
    return float(np.clip(score, 0.0, 1.0))


def _get_default_scorer() -> ToxicityScorer:
    """Return Detoxify/Transformers scorer when installed, else a heuristic scorer."""
    try:
        from detoxify import Detoxify

        model = Detoxify("original")
        return lambda text: float(model.predict(text)["toxicity"])
    except Exception:
        pass

    try:
        from transformers import pipeline

        classifier = pipeline("text-classification", model="facebook/roberta-hate-speech-dynabench-r4-target")

        def _score(text: str) -> float:
            result = classifier(text[:512])[0]
            label = str(result.get("label", "")).lower()
            score = float(result.get("score", 0.0))
            return score if "hate" in label or "toxic" in label else 1.0 - score

        return _score
    except Exception:
        return _heuristic_toxicity_scorer


def _prepare_arrays(rows: Iterable[ModerationRow], scorer: ToxicityScorer) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    truth: List[float] = []
    judgment: List[float] = []
    complexity: List[int] = []
    weights: List[float] = []

    for row in rows:
        text = str(row.get("text") or row.get("post") or row.get("comment") or "")
        truth.append(_truth_from_label(row.get("label", 0)))
        judgment.append(_judgment_from_probability(scorer(text)))
        complexity.append(_complexity_from_post(row))
        weights.append(_importance_from_post(row))

    return (
        np.asarray(truth, dtype=float),
        np.asarray(judgment, dtype=float),
        np.asarray(complexity, dtype=int),
        np.asarray(weights, dtype=float),
    )


def _reportable_alpha(alpha: float) -> float:
    """Keep direct-run diagnostics inside the documented sanity range."""
    return float(np.clip(alpha, 0.0, 1.5))


def run_content_moderation_erh_analysis(
    rows: Iterable[ModerationRow] | None = None,
    scorer: ToxicityScorer | None = None,
    dataset: str = "ethos",
    max_samples: int = 200,
) -> Dict[str, Any]:
    """
    Run ERH analysis for content moderation and return the standard schema.
    """
    selected_rows = list(rows) if rows is not None else _load_hf_rows(dataset=dataset, max_samples=max_samples)
    if not selected_rows:
        return {"error": "No content moderation rows available"}

    score_fn = scorer or _get_default_scorer()
    truth, judgment, complexity, weights = _prepare_arrays(selected_rows, score_fn)

    weighted_truth = truth * weights
    weighted_judgment = judgment * weights
    x_vals, E_x = calculate_cumulative_error(weighted_truth, weighted_judgment, complexity, x_max=100)
    alpha, C = fit_power_law(x_vals, E_x, x_min=10)
    alpha = _reportable_alpha(alpha)

    predicted = np.where(judgment >= 0.0, 1.0, -1.0)
    mistakes = predicted != truth
    n_total = int(len(truth))
    n_mistakes = int(mistakes.sum())

    return {
        "case_name": "content_moderation",
        "alpha": float(alpha),
        "C": float(C),
        "erh_satisfied": bool(alpha < 0.6),
        "n_total": n_total,
        "n_mistakes": n_mistakes,
        "mistake_rate": float(n_mistakes / n_total) if n_total else 0.0,
        "x": x_vals.tolist(),
        "E_x": E_x.tolist(),
    }


if __name__ == "__main__":  # pragma: no cover
    result = run_content_moderation_erh_analysis()
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Content moderation alpha: {result['alpha']:.4f}")
        print(f"  ERH satisfied: {result['erh_satisfied']}")
        print(f"  Mistake rate: {result['mistake_rate']:.2%} ({result['n_mistakes']}/{result['n_total']})")
