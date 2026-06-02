import json


def test_erh_case_comparison_summarizes_flat_and_grouped_cases(tmp_path):
    from simulation.real_data.erh_case_comparison import build_case_comparison

    results = {
        "truthfulqa": {"alpha": 0.4, "erh_satisfied": True, "mistake_rate": 0.2, "n_total": 10},
        "compas_by_race": {
            "groups": {
                "Black": {"alpha": 0.8, "erh_satisfied": False, "mistake_rate": 0.4, "n_total": 5},
                "White": {"alpha": 0.3, "erh_satisfied": True, "mistake_rate": 0.1, "n_total": 5},
            }
        },
        "llm_bias": {
            "pairs": {
                "White/Black": {"alpha": 0.9, "erh_satisfied": False, "mistake_rate": 1.0, "n_total": 2}
            }
        },
    }

    summary = build_case_comparison(results, output_json=tmp_path / "comparison.json")

    assert summary["case_name"] == "erh_case_comparison"
    assert summary["n_entries"] == 4
    assert summary["entries"][0]["name"] == "llm_bias:White/Black"
    assert summary["entries"][-1]["name"] == "compas_by_race:White"
    written = json.loads((tmp_path / "comparison.json").read_text(encoding="utf-8"))
    assert written["n_entries"] == 4


def test_erh_case_comparison_writes_bar_chart_when_requested(tmp_path):
    from simulation.real_data.erh_case_comparison import build_case_comparison

    chart_path = tmp_path / "alphas.png"
    summary = build_case_comparison(
        {"content_moderation": {"alpha": 0.55, "erh_satisfied": True, "mistake_rate": 0.25, "n_total": 20}},
        output_png=chart_path,
    )

    assert summary["n_entries"] == 1
    assert chart_path.exists()
    assert chart_path.stat().st_size > 0
