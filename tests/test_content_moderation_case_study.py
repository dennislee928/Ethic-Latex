import math

import numpy as np


def test_content_moderation_mapping_helpers_are_normalized():
    from simulation.real_data.content_moderation_case_study import (
        _complexity_from_post,
        _importance_from_post,
        _truth_from_label,
    )

    implicit = {
        "text": "Obviously just asking questions... those people never belong here.",
        "category": "implicit",
        "target_groups": ["protected"],
    }
    explicit = {"text": "short explicit slur", "category": "explicit", "label": 1}

    assert 1 <= _complexity_from_post(implicit) <= 100
    assert _complexity_from_post(implicit) > _complexity_from_post(explicit)
    assert _importance_from_post({"severity": "violence"}) == 4.0
    assert _importance_from_post(implicit) == 2.0
    assert _truth_from_label(1) == 1.0
    assert _truth_from_label(0) == -1.0


def test_run_content_moderation_erh_analysis_returns_standard_schema():
    from simulation.real_data.content_moderation_case_study import (
        run_content_moderation_erh_analysis,
    )

    rows = [
        {"text": "I hope they are attacked tonight", "label": 1, "severity": "violence"},
        {"text": "A direct slur should be moderated", "label": 1, "category": "slur"},
        {"text": "Welcome to the neighborhood", "label": 0, "category": "benign"},
        {"text": "Just joking... they never fit in here", "label": 1, "category": "implicit"},
        {"text": "Counter speech against hate", "label": 0, "category": "counter_speech"},
    ]

    def scorer(text: str) -> float:
        if "attacked" in text or "slur" in text:
            return 0.9
        if "joking" in text:
            return 0.2
        return 0.1

    result = run_content_moderation_erh_analysis(rows=rows, scorer=scorer)

    assert result["case_name"] == "content_moderation"
    assert math.isfinite(result["alpha"])
    assert math.isfinite(result["C"])
    assert isinstance(result["erh_satisfied"], bool)
    assert result["n_total"] == len(rows)
    assert result["n_mistakes"] == 1
    assert result["mistake_rate"] == 0.2
    assert len(result["x"]) == 100
    assert len(result["E_x"]) == 100
    assert np.all(np.isfinite(result["E_x"]))
