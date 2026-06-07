import math

import numpy as np
import pandas as pd


def _sample_medical_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [63, 41, 55, 38, 70, 45, 60, 50],
            "trestbps": [160, 120, 145, 118, 170, 125, 150, 122],
            "chol": [280, 190, 260, 180, 310, 205, 250, 195],
            "thalach": [95, 175, 120, 180, 88, 165, 110, 172],
            "oldpeak": [3.1, 0.2, 2.2, 0.1, 4.0, 0.5, 2.8, 0.3],
            "triage_level": ["critical", "non_urgent", "urgent", "non_urgent", "critical", "semi_urgent", "urgent", "non_urgent"],
            "target": [1, 0, 1, 0, 1, 0, 1, 0],
        }
    )


def test_clinical_complexity_counts_abnormal_values():
    from simulation.real_data.medical_triage_case_study import (
        DEFAULT_NORMAL_RANGES,
        _complexity_from_clinical,
        _importance_from_triage,
    )

    frame = _sample_medical_frame()
    high_complexity = _complexity_from_clinical(frame.iloc[0], DEFAULT_NORMAL_RANGES)
    low_complexity = _complexity_from_clinical(frame.iloc[1], DEFAULT_NORMAL_RANGES)

    assert 1 <= high_complexity <= 100
    assert 1 <= low_complexity <= 100
    assert high_complexity > low_complexity
    assert _importance_from_triage("critical") == 5.0
    assert _importance_from_triage("urgent") == 3.0
    assert _importance_from_triage("semi_urgent") == 1.5
    assert _importance_from_triage("non_urgent") == 1.0


def test_run_medical_triage_erh_analysis_returns_standard_schema():
    from simulation.real_data.medical_triage_case_study import run_medical_triage_erh_analysis

    result = run_medical_triage_erh_analysis(df=_sample_medical_frame())

    assert result["case_name"] == "medical_triage"
    assert math.isfinite(result["alpha"])
    assert math.isfinite(result["C"])
    assert isinstance(result["erh_satisfied"], bool)
    assert result["n_total"] > 0
    assert 0 <= result["n_mistakes"] <= result["n_total"]
    assert 0.0 <= result["mistake_rate"] <= 1.0
    assert len(result["x"]) == 100
    assert len(result["E_x"]) == 100
    assert np.all(np.isfinite(result["E_x"]))
