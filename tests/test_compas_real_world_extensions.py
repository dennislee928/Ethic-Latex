import math

import numpy as np
import pandas as pd


def _sample_compas_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "race": ["Black", "Black", "White", "White", "Black", "White"],
            "two_year_recid": [1, 0, 1, 0, 1, 0],
            "decile_score": [9, 3, 8, 2, 7, 4],
            "priors_count": [5, 0, 2, 1, 8, 0],
            "c_charge_degree": ["F", "M", "F", "M", "F", "M"],
            "days_b_screening_arrest": [10, 0, 8, 1, 30, 2],
        }
    )


def test_complexity_from_charge_uses_priors_charge_and_urgency():
    from simulation.real_data.compas_case_study import _complexity_from_charge

    df = _sample_compas_frame()
    complexity = _complexity_from_charge(df)

    assert complexity.dtype.kind in {"i", "u"}
    assert int(complexity.min()) >= 1
    assert int(complexity.max()) <= 100
    assert complexity.iloc[4] > complexity.iloc[1]
    assert complexity.iloc[0] > complexity.iloc[3]


def test_run_compas_by_race_returns_group_metrics():
    from simulation.real_data.compas_case_study import run_compas_by_race

    result = run_compas_by_race(_sample_compas_frame())

    assert result["case_name"] == "compas_by_race"
    assert result["n_groups"] == 2
    assert set(result["groups"]) == {"Black", "White"}
    for group in result["groups"].values():
        assert math.isfinite(group["alpha"])
        assert math.isfinite(group["C"])
        assert isinstance(group["erh_satisfied"], bool)
        assert group["n_total"] == 3
        assert 0.0 <= group["mistake_rate"] <= 1.0
        assert len(group["x"]) == 100
        assert len(group["E_x"]) == 100
        assert np.all(np.isfinite(group["E_x"]))
