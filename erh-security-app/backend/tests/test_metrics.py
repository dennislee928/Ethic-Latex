from app.erh_security.mapping import ErhSample
from app.erh_security.metrics import analyze_erh_structure, compute_delta, is_mistake


def test_delta_and_mistake_logic() -> None:
    s = ErhSample(complexity=10.0, ground_truth_value=-1.0, weight=1.0, judgment_value=1.0, action_id=1)
    delta = compute_delta(s)
    assert delta == 2.0
    assert is_mistake(s, tau=0.1) is True


def test_analyze_erh_structure_with_injected_functions() -> None:
    samples = [
        ErhSample(complexity=1.0, ground_truth_value=-1.0, weight=1.0, judgment_value=1.0, action_id=1),
        ErhSample(complexity=2.0, ground_truth_value=0.0, weight=2.0, judgment_value=0.0, action_id=2),
    ]

    def fake_select_primals(data):
        # pretend everything with is_mistake=True is a prime
        return [row for row in data if row[3]]

    def fake_pi_and_error(primes):
        return [1, 2, 3], [0.1, 0.2, 0.3]

    def fake_growth(error_curve):
        return {"alpha": 0.25, "r2": 0.99}

    result = analyze_erh_structure(
        samples,
        tau=0.0,
        select_primals=fake_select_primals,
        pi_and_error_fn=fake_pi_and_error,
        error_growth_fn=fake_growth,
    )

    assert result["num_samples"] == 2
    assert result["num_primes"] >= 1
    assert "pi_curve" in result and "error_curve" in result
    assert result["growth"]["alpha"] == 0.25


